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

# 📥 Save forwarded channel posts
@bot.on_message(filters.private & filters.forwarded & filters.incoming)
async def handle_forwarded_message(client, message):
    try:
        if message.forward_from_chat and message.forward_from_chat.type == "channel":
            original_channel = message.forward_from_chat
            file_name = message.caption.split("\n")[0] if message.caption else "No Caption"

            chat_id_str = str(original_channel.id)
            if chat_id_str.startswith("-100"):
                chat_id_str = chat_id_str[4:]

            telegram_link = f"https://t.me/c/{chat_id_str}/{message.forward_from_message_id}"

            doc = {
                "message_id": message.message_id,
                "file_name": file_name,
                "full_text": message.caption or "",
                "telegram_link": telegram_link
            }

            if collection.count_documents({"message_id": message.message_id}, limit=1) == 0:
                collection.insert_one(doc)
                logging.info(f"✅ Inserted: {file_name} -> {telegram_link}")
            else:
                logging.info(f"ℹ️ Already exists: {file_name} -> {telegram_link}")
    except Exception as e:
        logging.error(f"❌ Error processing message {message.message_id}: {e}")

# ---------------------------
bot.run()
