import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from config import BOT_TOKEN
from flask import Flask
import threading

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# GLOBAL BANWORD LIST
banwords = set()

# --- START MESSAGE WITH INLINE "ADD ME TO GROUP" ---
@bot.message_handler(commands=['start'])
def start_msg(msg):
    kb = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(
        "➕ Add Me To Your Group",
        url="https://t.me/GuardAntiAIBot?startgroup&admin=promote_members+delete_messages+restrict_members+invite_users+pin_messages+manage_video_chats"
    )
    kb.add(btn)

    bot.reply_to(
        msg,
        "👋 <b>GUARD ANTI-AI — GOD MODE READY</b>\n"
        "I protect your groups with ultra-aggressive AI scanning.",
        reply_markup=kb
    )

# --- ADMIN CHECK ---
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

# --- ADD BANWORD ---
@bot.message_handler(commands=['banword'])
def add_banword(msg):
    if not is_admin(msg.chat.id, msg.from_user.id):
        return bot.reply_to(msg, "⚠ Only admins can use this.")

    word = msg.text.replace("/banword", "").strip()
    if not word:
        return bot.reply_to(msg, "📌 Type a word: /banword <word>")

    banwords.add(word.lower())
    bot.reply_to(msg, f"🚫 Banword added: <b>{word}</b>")

# --- REMOVE BANWORD ---
@bot.message_handler(commands=['unbanword'])
def remove_banword(msg):
    if not is_admin(msg.chat.id, msg.from_user.id):
        return bot.reply_to(msg, "⚠ Only admins can use this.")

    word = msg.text.replace("/unbanword", "").strip()
    if not word:
        return bot.reply_to(msg, "📌 Type: /unbanword <word>")

    try:
        banwords.remove(word.lower())
        bot.reply_to(msg, f"✅ Removed banword: <b>{word}</b>")
    except:
        bot.reply_to(msg, "❌ Word not found.")

# --- SPAM FILTER ENGINE ---
def is_spam(text):
    if not text:
        return False

    # Banwords
    for w in banwords:
        if w in text.lower():
            return True

    # Links
    if re.search(r"(http|https|t\.me|\.com|www\.)", text):
        return True

    # Excessive Emoji
    if len(re.findall(r"[^\w\s,.!?]", text)) > 6:
        return True

    # CAPS Flood
    if sum(1 for c in text if c.isupper()) > 20:
        return True

    # Repeated characters
    if re.search(r"(.)\1{5,}", text):
        return True

    # Unicode obfuscation
    if re.search(r"[\u0336\u0335\u034f\u202e\u202d\u2066\u2067\u2068]", text):
        return True

    return False

# --- MAIN MESSAGE HANDLER ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def moder(msg):
    # Forwarded?
    if msg.forward_from or msg.forward_from_chat:
        bot.delete_message(msg.chat.id, msg.id)
        return

    # Text spam?
    if msg.text and is_spam(msg.text):
        try:
            bot.delete_message(msg.chat.id, msg.id)
            bot.restrict_chat_member(
                msg.chat.id,
                msg.from_user.id,
                until_date=3600 * 12
            )
        except:
            pass

# ------------- KEEPALIVE FOR RENDER -------------
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

print("🔥 GUARD ANTI-AI BOT RUNNING IN GOD MODE…")
bot.infinity_polling(skip_pending=True)
