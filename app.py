import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# --- Config ---
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
CHANNEL_ID = -1002479279470
CHANNEL_USERNAME = "moviestera1"

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Pyrogram Bot Client ---
bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MongoDB Connection ---
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client["lucas"]["Telegram_files"]

# --- Handlers ---
@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    count = collection.count_documents({})
    await message.reply_text(
        f"🎬 Welcome to Movie Bot!\n\n"
        f"🔍 Total Movies in DB: {count}\n"
        f"📣 Channel: @{CHANNEL_USERNAME}\n\n"
        f"Type a movie name to search!"
    )

@bot.on_message(filters.text & filters.group & ~filters.command("start"))
async def movie_search(_, message: Message):
    query = message.text.strip()
    logging.info(f"Searching for: {query}")
    results = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(5)

    found = False
    for doc in results:
        try:
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=doc["message_id"],
                reply_to_message_id=message.id
            )
            found = True
        except Exception as e:
            logging.error(f"Failed to copy: {e}")

    if not found:
        await message.reply("❌ Movie not found!", reply_to_message_id=message.id)

# --- Main ---
bot.run()
