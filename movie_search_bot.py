# --- movie_search_bot.py (for bot token with /start and movie search) ---

import logging
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
bot_token = "<your_bot_token>"
mongo_url = "<your_mongo_url>"
channel_username = "moviestera1"

client = MongoClient(mongo_url)
db = client["lucas"]
collection = db["Telegram_files"]

app = Client("movie_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    count = collection.count_documents({})
    await message.reply_text(
        f"**Welcome to Movie Search Bot!**\n\n"
        f"Channel: @{channel_username}\n"
        f"Movies in DB: {count}\n\n"
        "Just type the movie name to search."
    )

@app.on_message(filters.text & filters.group & ~filters.command(["start", "update", "fixfiles"]))
async def movie_search(_, message: Message):
    query = message.text.strip().lower()
    results = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(5)
    found = False
    for doc in results:
        msg_id = doc.get("message_id")
        if msg_id:
            try:
                await app.copy_message(message.chat.id, f"@{channel_username}", msg_id, reply_to_message_id=message.id)
                found = True
            except Exception as e:
                logging.error(f"Error sending message {msg_id}: {e}")
    if not found:
        await message.reply("Movie not found.", reply_to_message_id=message.id)

if __name__ == '__main__':
    app.run()
