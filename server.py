from flask import Flask, request
import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT ALIVE", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

bot.remove_webhook()
bot.set_webhook(url="https://YOUR-RENDER-URL.onrender.com/webhook")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
