import os
import threading
import logging
import re
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient, errors
from bson import ObjectId

# ---------------------------
# 🔧 CONFIG
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7778279666:AAGW8_ZODBU2othUTRIiLusCqmPROO_B1qg"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

# ---------------------------
# 🌐 Flask Web Server for Koyeb
app = Flask(__name__)
@app.route("/")
def home():
    return "🤖 Bot is alive!"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

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

# 🔍 Search with Inline Buttons
@bot.on_message(filters.text & ~filters.command(["start"]))
async def search_movie(client, message):
    query = message.text.strip()
    results = list(collection.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10))

    if not results:
        if message.chat.type == "private":
            await message.reply("❌ Movie not found.")
        else:
            hindi_msg = "❌ रिज़ल्ट नहीं मिला। कृपया पहले Google पर मूवी का नाम और रिलीज़ डेट चेक करें और वहाँ से कॉपी करके यहाँ पेस्ट करें।"
            await message.reply(hindi_msg)
        return

    buttons = []
    for doc in results:
        title = doc["file_name"][:60] + "..." if len(doc["file_name"]) > 60 else doc["file_name"]
        buttons.append([InlineKeyboardButton(text=title, callback_data=f"movie_{str(doc['_id'])}")])

    await message.reply(
        f"🔍 Found {len(results)} result(s). Click to view:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎬 Callback to show full movie info
@bot.on_callback_query(filters.regex(r"^movie_"))
async def send_movie_info(client, callback_query: CallbackQuery):
    try:
        movie_id = callback_query.data.split("_", 1)[1]
        result = collection.find_one({"_id": ObjectId(movie_id)})

        if not result:
            await callback_query.message.edit_text("❌ Movie not found.")
            return

        text = f"🎬 *{result.get('file_name')}*\n\n{result.get('text') or ''}"
        await callback_query.message.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Error: {e}")

# 💾 Save Forwarded Message
@bot.on_message(filters.forwarded & filters.private)
async def save_forwarded_message(client, message):
    try:
        full_caption = message.caption or "No Caption"
        file_name = full_caption.strip().splitlines()[0]

        # ✅ Extract first terabox link (for uniqueness)
        match = re.search(r'https?://(?:www\.)?[\w.]*terabox\.com/\S+', full_caption)
        telegram_link = match.group(0) if match else "N/A"

        # ⚠️ New logic: check based on file_name + telegram_link
        if collection.find_one({"file_name": file_name, "telegram_link": telegram_link}):
            await message.reply("⚠️ Already saved.")
            return

        collection.insert_one({
            "file_name": file_name,
            "text": full_caption,
            "telegram_link": telegram_link
        })

        await message.reply("✅ Movie info saved successfully.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ---------------------------
bot.run()
