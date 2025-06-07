import os
import threading
import logging
import re
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
# 🧼 Clean Unicode characters (… → , ’ → ', etc.)
def clean_text(text):
    if not text:
        return ""
    return text.replace("…", "").replace("’", "'").strip()

# ---------------------------
# 💬 /start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! ✅ I'm alive and running on Koyeb!")

# ---------------------------
# 🔍 Movie search (group + private)
@bot.on_message(filters.text & ~filters.command(["start"]))
async def search_movie(client, message):
    query = clean_text(message.text.strip())

    # Search in MongoDB with cleaned query
    result = collection.find_one({
        "$or": [
            {"file_name": {"$regex": re.escape(query), "$options": "i"}},
            {"text": {"$regex": re.escape(query), "$options": "i"}}
        ]
    })

    if result:
        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
    else:
        if message.chat.type == "private":
            text = "❌ Movie not found in database."
        else:
            return

    await message.reply_text(text, quote=True)

# ---------------------------
# 💾 Save forwarded message
@bot.on_message(filters.forwarded & filters.private)
async def save_forwarded_message(client, message):
    try:
        msg_id = message.forward_from_message_id or message.id
        full_caption = clean_text(message.caption or "No Caption")
        file_name = clean_text(full_caption.strip().splitlines()[0])

        # 🔗 Telegram Link or Terabox fallback
        if message.forward_from_chat and message.forward_from_message_id:
            chat_id = str(message.forward_from_chat.id)
            if chat_id.startswith("-100"):
                telegram_link = f"https://t.me/c/{chat_id[4:]}/{message.forward_from_message_id}"
            else:
                telegram_link = "N/A"
        else:
            match = re.search(r'https?://(?:www\.)?[\w.]*terabox\.com/\S+', full_caption)
            telegram_link = match.group(0) if match else "N/A"

        # ✅ Skip if already exists
        if collection.find_one({"message_id": msg_id}):
            await message.reply("⚠️ Already saved.")
            return

        # ✅ Save to MongoDB
        collection.insert_one({
            "message_id": msg_id,
            "file_name": file_name,
            "text": full_caption,
            "telegram_link": telegram_link
        })

        await message.reply("✅ Movie info saved successfully.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ---------------------------
bot.run()
