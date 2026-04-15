import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import json
import os
import re

# ------------- SETTINGS -------------
# TODO: USER WILL PROVIDE THE TOKEN
TOKEN = '8775597308:AAG9HPcYVoMMPj5qeBCVA1pIl65R5-LtiEc' 
# Assuming ADMIN_ID is the same as the main bot
ADMIN_ID = 7729481502

CONFIG_FILE = 'spam_config.json'

bot = telebot.TeleBot(TOKEN)

# In-memory session data for language and flow
user_state = {}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"dialogs": {}}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"dialogs": {}}

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

config = load_config()

# ------------- ADMIN MENU -------------
def show_admin_dialogs_menu(chat_id, update_msg_id=None):
    dialogs = config.get("dialogs", {})
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(InlineKeyboardButton("🔄 Обновить список (Refresh)", callback_data="admin_refresh"))
    
    # Sort dialogs: Unread first, then by last message timestamp
    has_dialogs = False
    for uid, d in dialogs.items():
        unread_count = d.get('unread_by_admin', 0)
        mark = "🔴" if unread_count > 0 else "⚪"
        username = d.get('username', f"User {uid}")
        
        btn_text = f"{mark} {username} (Unread: {unread_count})"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"admin_view_{uid}"))
        has_dialogs = True
            
    text = "🛠 <b>Панель Поддержки (СпамБот)</b>\n\nСписок текущих диалогов с пользователями:" if has_dialogs else "🛠 <b>Панель Поддержки</b>\n\nНет активных диалогов."
    
    if update_msg_id:
        try:
            bot.edit_message_text(text, chat_id, update_msg_id, reply_markup=markup, parse_mode='HTML')
        except:
            pass
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_callbacks(call):
    if call.message.chat.id != ADMIN_ID: return
    action = call.data
    
    if action == "admin_refresh":
        show_admin_dialogs_menu(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Обновлено ✅")
        
    elif action.startswith("admin_view_"):
        uid = action.split("_")[2]
        d = config["dialogs"].get(uid)
        if not d:
            bot.answer_callback_query(call.id, "Диалог не найден.")
            return
            
        d['unread_by_admin'] = 0
        save_config(config)
        
        # Build message history string
        history = "\n".join(d.get('history', [])[-10:]) # Show last 10 msgs
        
        text = (
            f"📨 <b>Диалог с {d.get('username')}</b> <i>(ID: {uid})</i>\n\n"
            f"<b>Последние сообщения:</b>\n{history}\n\n"
            f"<i>💡 Чтобы ответить, сделайте Reply (Ответить) на это сообщение.</i>"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Назад к списку", callback_data="admin_refresh"))
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')


# ------------- USER MESSAGE HANDLER -------------
@bot.message_handler(func=lambda m: True)
def router(message):
    chat_id = message.chat.id
    text = message.text
    
    # 1. Admin Commands
    if chat_id == ADMIN_ID:
        if text == "/admin" or text == "/start":
            show_admin_dialogs_menu(chat_id)
            return
            
        if message.reply_to_message:
            original = message.reply_to_message.text
            match = re.search(r"\(ID:\s*(\d+)\)", original)
            if match:
                target_uid = match.group(1)
                
                # Append to history
                if target_uid in config["dialogs"]:
                    config["dialogs"][target_uid].setdefault("history", []).append(f"👨‍💻 Админ: {text}")
                    save_config(config)
                    
                try:
                    bot.send_message(target_uid, f"👨‍💻 Support:\n\n{text}")
                    bot.send_message(ADMIN_ID, "✅ Ответ отправлен.")
                except:
                    bot.send_message(ADMIN_ID, "❌ Ошибка отправки (пользователь заблокировал бота?).")
                return

    # 2. User UserFlow
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    if text == "/start":
        user_state[chat_id] = {'stage': 'lang'}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("English 🇬🇧"), KeyboardButton("Español 🇪🇸"))
        bot.send_message(chat_id, "Welcome / Bienvenido.\n\nPlease choose your language / Por favor, elige tu idioma:", reply_markup=markup)
        return
        
    state = user_state.get(chat_id, {}).get('stage')
    
    if state == 'lang':
        lang = "ES" if "español" in text.lower() else "EN"
        user_state[chat_id] = {'stage': 'chat', 'lang': lang}
        
        if lang == "ES":
            bot.send_message(chat_id, "Por favor, describa su problema. El soporte le responderá pronto.", reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(chat_id, "Please describe your issue. Support will reply to you shortly.", reply_markup=ReplyKeyboardRemove())
        return

    # Any other generic message gets added to history and prompts admin
    uid_str = str(chat_id)
    if uid_str not in config["dialogs"]:
        config["dialogs"][uid_str] = {
            "username": username,
            "unread_by_admin": 0,
            "history": []
        }
        
    config["dialogs"][uid_str]["unread_by_admin"] += 1
    config["dialogs"][uid_str]["history"].append(f"👤 User: {text}")
    save_config(config)
    
    lang = user_state.get(chat_id, {}).get('lang', 'EN')
    if lang == "ES":
        bot.send_message(chat_id, "✅ Mensaje enviado al soporte.")
    else:
        bot.send_message(chat_id, "✅ Message sent to support.")

if __name__ == "__main__":
    print("Spam Support Bot is running...")
    bot.infinity_polling()
