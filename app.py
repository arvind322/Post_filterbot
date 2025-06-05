import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pymongo import MongoClient

# ---------------------------
# 🔧 CONFIGURATION
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
CHANNEL_USERNAME = "moviestera1"  # Without @

# ---------------------------
# 🌐 Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ---------------------------
# 📦 MongoDB Setup
mongo = MongoClient(MONGO_URI)
db = mongo["lucas"]
collection = db["Telegram_files"]

# ---------------------------
# 🤖 Telegram Bot Setup
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------------------
# /start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! ✅ I'm alive and running on Koyeb!")

# ---------------------------
# /update command: Fetch from channel and insert into MongoDB
@bot.on_message(filters.command("update"))
async def update_db(client, message):
    count = 0
    async for msg in bot.get_chat_history(CHANNEL_USERNAME):
        if msg.document or msg.video or msg.audio:
            file_id = (
                msg.document.file_id if msg.document else
                msg.video.file_id if msg.video else
                msg.audio.file_id
            )

            original_file_name = (
                msg.document.file_name if msg.document else
                msg.video.file_name if msg.video else
                msg.audio.file_name
            )

            caption = msg.caption or ""
            file_name = caption.splitlines()[0] if caption else original_file_name

            # Skip duplicates
            if not collection.find_one({"file_id": file_id}):
                collection.insert_one({
                    "file_id": file_id,
                    "file_name": file_name,
                    "original_file_name": original_file_name,
                    "text": caption
                })
                count += 1

    await message.reply_text(f"✅ Update completed. {count} new items added.")

# ---------------------------
# Movie Search
@bot.on_message(filters.text & ~filters.command(["start", "update"]))
async def search_movie(client, message):
    query = message.text.strip()

    result = collection.find_one({
        "file_name": {"$regex": f".*{query}.*", "$options": "i"}
    })

    if result:
        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
        await message.reply_text(text, quote=True, parse_mode="markdown")
    else:
        if message.chat.type == "private":
            await message.reply_text("❌ Movie not found in database.", quote=True)

# ---------------------------
bot.run()
