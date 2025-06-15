
import telebot
import json
import datetime
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [622590155, 76437016]
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"tasks": {}, "submissions": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Himmat bot ishga tushdi.")

@bot.message_handler(commands=["vazifa"])
def set_task(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = message.text.replace("/vazifa", "").strip()
    if not text:
        bot.reply_to(message, "Vazifa matnini yozing: /vazifa Bugun 3 sahifa Qur’on o‘qilsin.")
        return
    today = str(datetime.date.today())
    data = load_data()
    data["tasks"][today] = text
    data["submissions"][today] = []
    save_data(data)
    bot.send_message(message.chat.id, f"📌 Bugungi vazifa:
{text}")

@bot.message_handler(commands=["bajardim"])
def mark_done(message):
    user_id = message.from_user.id
    today = str(datetime.date.today())
    data = load_data()
    if today not in data["tasks"]:
        bot.reply_to(message, "Bugungi kun uchun vazifa belgilanmagan.")
        return
    if user_id not in data["submissions"].get(today, []):
        data["submissions"][today].append(user_id)
        save_data(data)
        bot.reply_to(message, "✅ Vazifani bajarganingiz qayd etildi.")
    else:
        bot.reply_to(message, "Siz allaqachon bajarganingizni bildirgansiz.")

@bot.message_handler(commands=["hisobot"])
def report(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    today = str(datetime.date.today())
    data = load_data()
    task = data["tasks"].get(today)
    submitted = data["submissions"].get(today, [])
    chat_id = message.chat.id

    if not task:
        bot.send_message(chat_id, "Bugungi vazifa belgilanmagan.")
        return

    try:
        members = bot.get_chat_administrators(chat_id)
        member_ids = [admin.user.id for admin in members if not admin.user.is_bot]
    except Exception as e:
        bot.send_message(chat_id, f"Hisobot olishda xatolik: {e}")
        return

    bajarganlar = [uid for uid in submitted if uid in member_ids]
    bajarmaganlar = [uid for uid in member_ids if uid not in submitted]

    text = f"📊 Hisobot - {today}\n\n"
    text += f"✅ Bajarganlar: {len(bajarganlar)} ta\n"
    text += f"❌ Bajarmaganlar: {len(bajarmaganlar)} ta\n\n"

    if len(bajarmaganlar) == 0:
        text += "🎉 Barchasi bajardi! Barakalla!"
    else:
        text += "⚠️ Quyidagilar bajarmagan:\n" + "\n".join([str(uid) for uid in bajarmaganlar])

    bot.send_message(chat_id, text)

bot.polling()
