from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pymongo import MongoClient

API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Initialize Pyrogram bot
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["lucas"]  # Changed from 'telegram' to 'lucas'
collection = db["Telegram_files"]  # Changed collection name as per your comment

@bot.on_message(filters.private & filters.text)
async def handle_message(client, message):
    doc = {
        "user_id": message.from_user.id,
        "text": message.text,
        "message_id": message.id
    }
    collection.insert_one(doc)
    await message.reply("Message saved to MongoDB!")

# Threaded Flask server
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Threaded Pyrogram bot
def run_bot():
    bot.run()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    Thread(target=run_bot).start()
