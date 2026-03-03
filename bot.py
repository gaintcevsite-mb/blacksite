import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import re

TOKEN = '8464446592:AAHz5xhjTiiSWX1cPuVvU6yfUzOBPQLTdvw'
ADMIN_ID = 8253241623
CONFIG_FILE = 'bot_config.json'

bot = telebot.TeleBot(TOKEN)

# In-memory storage for User and Admin Flows
user_data = {}
admin_state = {}

# --- Configuration Management ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            if "users" not in cfg:
                cfg["users"] = []
            return cfg
    return {"countries": {}, "users": []}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

bot_config = load_config()

# --- Helper Keyboards ---
def create_reply_keyboard(options):
    if not options:
        return ReplyKeyboardRemove()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    return markup

# --- Global Message Handler (State Machine) ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
def global_text_router(message):
    chat_id = message.chat.id
    text = message.text
    
    # 1. Admin Reply Intercept
    if chat_id == ADMIN_ID and message.reply_to_message is not None:
        return admin_reply_handler(message)
        
    # 2. Start Command Intercept (Resets everything)
    if text.startswith('/start'):
        # Clear any existing state safely
        if chat_id in user_data:
            del user_data[chat_id]
        if chat_id in admin_state:
             del admin_state[chat_id]
             
        args = text.split()
        deep_link_country = None
        if len(args) > 1:
            param = args[1]
            if param.startswith('join_'):
                deep_link_country = param[5:] # e.g., Pakistan
                
        user_data[chat_id] = {'username': message.from_user.username, 'answers': {}, 'state': 'init'}
        
        # Track unique user
        user_exists = any(u.get('chat_id') == chat_id for u in bot_config['users'])
        if not user_exists:
            bot_config['users'].append({
                'chat_id': chat_id,
                'username': message.from_user.username
            })
            save_config(bot_config)
        
        # Smart Country Matching (handle emojis in configured names)
        matched_country = None
        if deep_link_country:
            available_countries = list(bot_config.get('countries', {}).keys())
            search_str = deep_link_country.replace('_', ' ').lower()
            for conf_c in available_countries:
                if search_str in conf_c.lower():
                    matched_country = conf_c
                    break
                    
        if matched_country:
            user_data[chat_id]['country'] = matched_country
            start_country_flow(chat_id, matched_country)
        else:
            available_countries = list(bot_config.get('countries', {}).keys())
            if not available_countries:
                bot.send_message(chat_id, "Welcome to PayForge! Applications are currently closed.")
                return
            
            user_data[chat_id]['state'] = 'awaiting_country'
            bot.send_message(
                chat_id,
                "Welcome to PayForge!\n\nPlease select your country to apply:",
                reply_markup=create_reply_keyboard(available_countries)
            )
        return

    # 3. Admin Command Intercept
    if text == '/admin':
        if chat_id == ADMIN_ID:
            # Clear admin text state just in case
            if chat_id in admin_state:
                del admin_state[chat_id]
            show_admin_menu(chat_id)
        return

    # 4. Admin Setup States (Adding things)
    if chat_id in admin_state:
        state_obj = admin_state[chat_id]
        action = state_obj.get('action')
        
        if action == 'add_country':
            process_add_country(message)
            return
        elif action == 'add_q_text':
            process_add_question_text(message)
            return
        elif action == 'add_q_options':
            process_add_question_options(message)
            return
        elif action == 'add_q_cond_ask':
            process_cond_ask(message)
            return
        elif action == 'add_q_cond_select':
            process_cond_select(message)
            return
        elif action == 'add_q_cond_value':
            process_cond_value(message)
            return
        elif action == 'broadcast_msg':
            process_broadcast_msg(message)
            return
        elif action == 'edit_q_text':
            process_edit_q_text(message)
            return
        elif action == 'edit_q_options':
            process_edit_q_options(message)
            return

    # 5. Normal User Questionnaire States
    if chat_id in user_data:
        curr_state = user_data[chat_id].get('state')
        
        if curr_state == 'awaiting_country':
            process_country_selection(message)
            return
        elif curr_state == 'awaiting_name':
            process_name(message)
            return
        elif curr_state == 'awaiting_dynamic_answer':
            process_dynamic_answer(message)
            return


# --- Core User Flow Functions ---

def process_country_selection(message):
    chat_id = message.chat.id
    country = message.text
    if country not in bot_config.get('countries', {}):
        bot.send_message(chat_id, "Please select a valid country from the keyboard.")
        return
        
    user_data[chat_id]['country'] = country
    start_country_flow(chat_id, country)

def start_country_flow(chat_id, country):
    user_data[chat_id]['current_q_index'] = -1
    user_data[chat_id]['state'] = 'awaiting_name'
    
    bot.send_message(
        chat_id, 
        f"You are applying as a partner for {country}.\n\nPlease enter your full name:",
        reply_markup=ReplyKeyboardRemove()
    )

def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    ask_next_question(chat_id)

def ask_next_question(chat_id):
    data = user_data.get(chat_id)
    if not data: return
    
    country = data.get('country')
    questions = bot_config.get('countries', {}).get(country, [])
    
    next_index = data['current_q_index'] + 1
    
    while next_index < len(questions):
        q = questions[next_index]
        condition = q.get('condition')
        
        if condition:
            dep_index = condition.get('depends_on_index')
            expected = condition.get('expected_answer')
            actual_answer = data['answers'].get(str(dep_index))
            if actual_answer != expected:
                next_index += 1
                continue 
        break 
        
    if next_index >= len(questions):
        finish_application(chat_id)
        return
        
    data['current_q_index'] = next_index
    data['state'] = 'awaiting_dynamic_answer'
    q = questions[next_index]
    
    bot.send_message(
        chat_id, 
        q['text'],
        reply_markup=create_reply_keyboard(q.get('options', []))
    )

def process_dynamic_answer(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id)
    if not data: return
    
    q_index = data['current_q_index']
    data['answers'][str(q_index)] = message.text
    
    ask_next_question(chat_id)

def finish_application(chat_id):
    data = user_data.get(chat_id, {})
    country = data.get('country', 'Unknown')
    name = data.get('name', 'Unknown')
    username = f"@{data.get('username')}" if data.get('username') else "No username"
    
    del user_data[chat_id] # Clean up state fully
    
    bot.send_message(
        chat_id, 
        "Thank you! Your application has been submitted successfully. Our team will contact you soon.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    questions = bot_config.get('countries', {}).get(country, [])
    
    answers_text = ""
    for i, q in enumerate(questions):
        ans = data.get('answers', {}).get(str(i))
        if ans: 
            answers_text += f"🔹 <b>{q['text']}</b>\n{ans}\n\n"
            
    admin_text = (
        f"🚨 <b>Новая заявка PayForge: {country}</b> 🚨\n"
        f"<i>(ID: {chat_id})</i>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Telegram:</b> {username}\n\n"
        f"<b>Анкета:</b>\n"
        f"{answers_text}"
        f"<i>💡 Чтобы ответить пользователю, просто свайпните влево и сделайте Reply на это сообщение!</i>"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode='HTML')
    except Exception as e:
        print(f"Failed to send admin message: {e}")

# --- Two-way Messaging ---
def admin_reply_handler(message):
    original_text = message.reply_to_message.text
    if not original_text: return
    
    match = re.search(r"\(ID:\s*(\d+)\)", original_text)
    if match:
        user_chat_id = int(match.group(1))
        reply_text = f"✉️ <b>Сообщение от Администратора:</b>\n\n{message.text}"
        try:
            bot.send_message(user_chat_id, reply_text, parse_mode='HTML')
            bot.send_message(ADMIN_ID, "✅ Ответ отправлен.")
        except Exception:
            bot.send_message(ADMIN_ID, "❌ Ошибка при отправке ответа.")

# --- Admin Panel (Dynamic Constructor) ---

def show_admin_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📌 Управление странами", callback_data="admin_countries"),
        InlineKeyboardButton("📢 Рассылка (Broadcast)", callback_data="admin_broadcast"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    )
    bot.send_message(chat_id, "🛠 <b>Панель Администратора</b>\nВыберите опцию для управления:", reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_callbacks(call):
    if call.message.chat.id != ADMIN_ID: return
    
    action = call.data
    
    if action == "admin_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_admin_menu(call.message.chat.id)
        
    elif action == "admin_countries":
        show_countries_list(call.message.chat.id, call.message.message_id)
        
    elif action == "admin_stats":
        total_users = len(bot_config.get('users', []))
        total_countries = len(bot_config.get('countries', {}))
        stats_text = (
            f"📊 <b>Статистика Бота</b>\n\n"
            f"👥 Уникальных пользователей: <b>{total_users}</b>\n"
            f"🌍 Настроено стран: <b>{total_countries}</b>\n"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, stats_text, parse_mode='HTML')

    elif action == "admin_broadcast":
        if not bot_config.get('users'):
             bot.answer_callback_query(call.id, "Нет пользователей для рассылки.", show_alert=True)
             return
             
        admin_state[call.message.chat.id] = {'action': 'broadcast_msg'}
        bot.send_message(call.message.chat.id, "Отправьте текст сообщения для рассылки всем пользователям бота (или напишите 'отмена'):")
        
    elif action == "admin_add_country":
        admin_state[call.message.chat.id] = {'action': 'add_country'}
        bot.send_message(call.message.chat.id, "Введите точное название новой страны (например, 'Индия'):")
        
    elif action.startswith("admin_editcountry_"):
        country = action.split("_")[2]
        show_country_editor(call.message.chat.id, call.message.message_id, country)
        
    elif action.startswith("admin_delcountry_"):
        country = action.split("_")[2]
        if country in bot_config['countries']:
            del bot_config['countries'][country]
            save_config(bot_config)
            bot.answer_callback_query(call.id, f"Deleted {country}")
            show_countries_list(call.message.chat.id, call.message.message_id)
            
    elif action.startswith("admin_addq_"):
        country = action.split("_")[2]
        admin_state[call.message.chat.id] = {'action': 'add_q_text', 'country': country}
        bot.send_message(call.message.chat.id, f"Добавление вопроса для {country}.\nВведите текст нового вопроса:")
        
    elif action.startswith("admin_editqsub_"):
        parts = action.split("_")
        country = parts[2]
        q_index = int(parts[3])
        show_q_edit_menu(call.message.chat.id, call.message.message_id, country, q_index)

    elif action.startswith("admin_editqtext_"):
        parts = action.split("_")
        country = parts[2]
        q_index = int(parts[3])
        admin_state[call.message.chat.id] = {'action': 'edit_q_text', 'country': country, 'q_index': q_index}
        bot.send_message(call.message.chat.id, "Введите новый текст вопроса:")

    elif action.startswith("admin_editqopt_"):
        parts = action.split("_")
        country = parts[2]
        q_index = int(parts[3])
        admin_state[call.message.chat.id] = {'action': 'edit_q_options', 'country': country, 'q_index': q_index}
        bot.send_message(call.message.chat.id, "Введите новые кнопки через слэш (Например: 'Да/Нет') или 'NONE':")
        
    elif action.startswith("admin_delq_"):
        parts = action.split("_")
        country = parts[2]
        q_index = int(parts[3])
        if country in bot_config['countries']:
            if 0 <= q_index < len(bot_config['countries'][country]):
                bot_config['countries'][country].pop(q_index)
                save_config(bot_config)
                bot.answer_callback_query(call.id, "Вопрос удален.")
                show_country_editor(call.message.chat.id, call.message.message_id, country)

def show_countries_list(chat_id, message_id):
    markup = InlineKeyboardMarkup()
    for country in bot_config.get('countries', {}):
        markup.add(
            InlineKeyboardButton(f"📝 {country}", callback_data=f"admin_editcountry_{country}"),
            InlineKeyboardButton(f"❌ Del", callback_data=f"admin_delcountry_{country}")
        )
    markup.add(InlineKeyboardButton("➕ Add New Country", callback_data="admin_add_country"))
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="admin_menu"))
    
    bot.edit_message_text("🌍 <b>Manage Countries</b>\nSelect a country to edit its questionnaire:", 
                          chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode='HTML')

def process_add_country(message):
    chat_id = message.chat.id
    country = message.text.strip()
    if country not in bot_config['countries']:
        bot_config['countries'][country] = []
        save_config(bot_config)
        bot.send_message(chat_id, f"✅ Added {country}.")
    else:
        bot.send_message(chat_id, f"⚠️ Country {country} already exists.")
    
    del admin_state[chat_id]
    show_admin_menu(chat_id)

def show_country_editor(chat_id, message_id, country):
    questions = bot_config.get('countries', {}).get(country, [])
    
    markup = InlineKeyboardMarkup()
    text = f"📍 <b>Анкета: {country}</b>\n\n"
    
    if not questions:
        text += "<i>Вопросов пока нет. Юзера спросят только Имя.</i>"
    else:
        for i, q in enumerate(questions):
            opts = "/".join(q.get('options', [])) if q.get('options') else "Свободный текст"
            cond = f" (Зависит от Вопроса {q['condition']['depends_on_index']+1})" if q.get('condition') else ""
            text += f"<b>В{i+1}:</b> {q['text']}\n<i>Кнопки: {opts}</i>{cond}\n\n"
            markup.add(InlineKeyboardButton(f"⚙️ В{i+1}", callback_data=f"admin_editqsub_{country}_{i}"))
            
    markup.add(InlineKeyboardButton("➕ Add New Question", callback_data=f"admin_addq_{country}"))
    markup.add(InlineKeyboardButton("🔙 Back to Countries", callback_data="admin_countries"))
    
    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode='HTML')

def show_q_edit_menu(chat_id, message_id, country, q_index):
    q = bot_config['countries'][country][q_index]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏️ Изменить текст", callback_data=f"admin_editqtext_{country}_{q_index}"))
    markup.add(InlineKeyboardButton("🔘 Изменить кнопки", callback_data=f"admin_editqopt_{country}_{q_index}"))
    markup.add(InlineKeyboardButton("❌ Удалить вопрос", callback_data=f"admin_delq_{country}_{q_index}"))
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data=f"admin_editcountry_{country}"))
    
    bot.edit_message_text(f"Редактирование В{q_index+1}:\n<b>{q['text']}</b>", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode='HTML')

def process_edit_q_text(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    bot_config['countries'][state['country']][state['q_index']]['text'] = message.text
    save_config(bot_config)
    bot.send_message(chat_id, "✅ Текст сохранен.")
    country = state['country']
    del admin_state[chat_id]
    
    # Needs a new message because we can't edit previous from a standard text handler easily without passing message_id
    show_admin_menu(chat_id)
    bot.send_message(chat_id, f"Продолжить настройку: /{state['country']} (через меню)")

def process_edit_q_options(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    
    opts_input = message.text.strip()
    if opts_input.upper() == 'NONE':
        options = []
    else:
        options = [o.strip() for o in opts_input.split('/')]
        
    bot_config['countries'][state['country']][state['q_index']]['options'] = options
    save_config(bot_config)
    bot.send_message(chat_id, "✅ Кнопки сохранены.")
    del admin_state[chat_id]
    show_admin_menu(chat_id)

def process_add_question_text(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    if not state: return
    
    state['q_text'] = message.text
    state['action'] = 'add_q_options'
    
    bot.send_message(
        chat_id, 
        "Great. Do you want to provide specific button options for the user? (e.g., 'Yes / No').\n\nType the options separated by a slash '/'. Or type 'NONE' to allow them to type a free-text answer."
    )

def process_add_question_options(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    
    opts_input = message.text.strip()
    if opts_input.upper() == 'NONE':
        options = []
    else:
        options = [o.strip() for o in opts_input.split('/')]
        
    state['q_options'] = options
    state['action'] = 'add_q_cond_ask'
    
    bot.send_message(
        chat_id, 
        "Должен ли этот вопрос появляться ТОЛЬКО если юзер дал определенный ответ на ПРЕДЫДУЩИЙ вопрос?",
        reply_markup=create_reply_keyboard(["Да", "Нет"])
    )

def process_cond_ask(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    answer = message.text.lower()
    
    if answer == 'нет' or answer == 'no':
        save_new_question(chat_id)
    else:
        country = state['country']
        questions = bot_config.get('countries', {}).get(country, [])
        if not questions:
            bot.send_message(chat_id, "Это первый вопрос, поэтому он не может зависеть от предыдущих.", reply_markup=ReplyKeyboardRemove())
            save_new_question(chat_id)
            return
            
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        text = "От какого вопроса он зависит?\n\n"
        for i, q in enumerate(questions):
            text += f"В{i+1}: {q['text']}\n"
            markup.add(KeyboardButton(f"В{i+1}"))
            
        state['action'] = 'add_q_cond_select'
        bot.send_message(chat_id, text, reply_markup=markup)

def process_cond_select(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    
    match = re.search(r"В(\d+)", message.text)
    if not match:
        match = re.search(r"Q(\d+)", message.text) # Fallback if manual entry
    if not match:
        bot.send_message(chat_id, "Неверный выбор. Пожалуйста, используйте кнопки.")
        return
        
    q_index = int(match.group(1)) - 1
    state['cond_depends_on'] = q_index
    state['action'] = 'add_q_cond_value'
    
    bot.send_message(chat_id, "Введите ТОЧНЫЙ текст ответа, который должен послужить триггером для показа этого вопроса (например: 'Да'):", reply_markup=ReplyKeyboardRemove())

def process_cond_value(message):
    chat_id = message.chat.id
    state = admin_state.get(chat_id)
    
    state['cond_expected_value'] = message.text.strip()
    save_new_question(chat_id)

def save_new_question(chat_id):
    state = admin_state.get(chat_id)
    country = state['country']
    
    new_q = {
        "text": state['q_text'],
        "options": state['q_options']
    }
    
    if 'cond_depends_on' in state and 'cond_expected_value' in state:
        new_q['condition'] = {
            "depends_on_index": state['cond_depends_on'],
            "expected_answer": state['cond_expected_value']
        }
    
    bot_config['countries'][country].append(new_q)
    save_config(bot_config)
    
    bot.send_message(chat_id, "✅ Вопрос успешно добавлен. Откройте меню стран (управление) чтобы продолжить редактирование списка.", reply_markup=ReplyKeyboardRemove())
    
    del admin_state[chat_id]
    show_admin_menu(chat_id)

def process_broadcast_msg(message):
    chat_id = message.chat.id
    if message.text.lower().strip() == 'отмена':
        del admin_state[chat_id]
        bot.send_message(chat_id, "❌ Рассылка отменена.")
        show_admin_menu(chat_id)
        return
        
    users = bot_config.get('users', [])
    success_count = 0
    
    bot.send_message(chat_id, f"Начинаю рассылку для {len(users)} пользователей...")
    
    for user in users:
        try:
            bot.send_message(user['chat_id'], message.text, parse_mode='HTML')
            success_count += 1
        except Exception as e:
            print(f"Failed to send broadcast to {user['chat_id']}: {e}")
            
    bot.send_message(chat_id, f"✅ Рассылка завершена.\nУспешно отправлено: {success_count} / {len(users)}")
    del admin_state[chat_id]
    show_admin_menu(chat_id)

if __name__ == '__main__':
    print("PayForge Bot is running...")
    bot.infinity_polling(skip_pending=True)
