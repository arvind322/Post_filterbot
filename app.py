from pyrogram import Client
from pymongo import MongoClient
import asyncio

# Telegram credentials
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"

# MongoDB setup
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["lucas"]
collection = db["Telegram_files"]

# Telegram channel username (without @)
CHANNEL_USERNAME = "moviestera1"

# Pyrogram client
app = Client("channel_scraper", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def fetch_and_save_messages():
    async with app:
        async for message in app.get_chat_history(CHANNEL_USERNAME):
            if not message.text and not message.caption:
                continue  # Skip empty

            message_id = message.id
            full_text = message.caption or message.text or ""
            lines = full_text.strip().split("\n")
            file_name = lines[0].strip() if lines else ""

            telegram_link = f"https://t.me/{CHANNEL_USERNAME}/{message_id}"

            # Skip duplicates
            if collection.find_one({"message_id": message_id}):
                print(f"⏭️ Skipped (duplicate): {message_id}")
                continue

            doc = {
                "message_id": message_id,
                "file_name": file_name,
                "text": full_text,
                "telegram_link": telegram_link
            }

            collection.insert_one(doc)
            print(f"✅ Inserted: {file_name} -> {telegram_link}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save_messages())
