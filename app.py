from flask import Flask
from threading import Thread
from pyrogram import Client, filters, idle
from pymongo import MongoClient
import asyncio

API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

# Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Pyrogram setup
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["lucas"]
collection = db["Telegram_files"]

@bot.on_message(filters.private & filters.text)
async def handle_message(client, message):
    doc = {
        "user_id": message.from_user.id,
        "text": message.text,
        "message_id": message.id
    }
    collection.insert_one(doc)
    await message.reply("Message saved to MongoDB!")

# Run Flask in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Run the bot properly with asyncio in the main thread
async def run_bot():
    await bot.start()
    print("Bot started...")
    await idle()
    await bot.stop()
    print("Bot stopped...")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
