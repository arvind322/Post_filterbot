import os
import threading
import logging
from flask import Flask
from pyrogram import Client, filters
from pymongo import MongoClient, errors

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
# 🧠 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------
# 🤖 Telegram Bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------------------
# 🍿 MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['lucas']
    collection = db['Telegram_files']
    logging.info("✅ Connected to MongoDB")
except errors.ServerSelectionTimeoutError:
    logging.error("❌ Cannot connect to MongoDB. Check your URI and network.")
    exit(1)

# ---------------------------
# 💬 /start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! ✅ I'm alive and running on Koyeb!")

# 🎬 Movie search (group + private)
@bot.on_message(filters.text & ~filters.command(["start"]))
async def search_movie(client, message):
    query = message.text.strip()

    # Search in MongoDB
    result = collection.find_one({
        "file_name": {"$regex": query, "$options": "i"}
    })

    if result:
        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
    else:
        if message.chat.type == "private":
            text = "❌ Movie not found in database."
        else:
            return

    await message.reply_text(text, quote=True)

@bot.on_message(filters.forwarded & filters.private)
async def save_forwarded_message(client, message):
    try:
        msg_id = message.forward_from_message_id or message.message_id
        file_name = message.caption.splitlines()[0] if message.caption else "No Caption"
        full_caption = message.caption or "No Caption"
        telegram_link = f"https://t.me/c/{str(message.forward_from_chat.id)[4:]}/{msg_id}" if message.forward_from_chat else "N/A"

        # Check if already exists
        if collection.find_one({"message_id": msg_id}):
            await message.reply("⚠️ Already saved.")
            return

        collection.insert_one({
            "message_id": msg_id,
            "file_name": file_name,
            "caption": full_caption,
            "telegram_link": telegram_link
        })

        await message.reply("✅ Movie info saved successfully.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
# ---------------------------
bot.run()
