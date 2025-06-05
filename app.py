import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pymongo import MongoClient

# ---------------------------
# 🔧 CONFIG (Your credentials)
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

# ---------------------------
# 🌐 Flask Web Server for Koyeb
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ---------------------------
# 🤖 Telegram Bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------------------
# 🍿 MongoDB
client = MongoClient(MONGO_URI)
db = client['lucas']
collection = db['Telegram_files']

# ---------------------------
# 💬 /start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! ✅ I'm alive and running on Koyeb!")

@bot.on_message(filters.text & ~filters.command(["start", "update"]))
async def search_movie(client, message):
    query = message.text.strip()

    # ✅ Improved regex for partial match
    result = collection.find_one({
        "file_name": {"$regex": f".*{query}.*", "$options": "i"}
    })

    if result:
        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
        await message.reply_text(text, quote=True, parse_mode="markdown")
    else:
        if message.chat.type == "private":
            await message.reply_text("❌ Movie not found in database.", quote=True)
# 🎬 Movie search (group + private)
@bot.on_message(filters.text & ~filters.command(["start", "update"]))
async def search_movie(client, message):
    query = message.text.strip()

    result = collection.find_one({
        "file_name": {"$regex": query, "$options": "i"}
    })

    if result:
        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
        await message.reply_text(text, quote=True, parse_mode="markdown")
    else:
        if message.chat.type == "private":
            await message.reply_text("❌ Movie not found in database.", quote=True)

# ---------------------------
bot.run()
