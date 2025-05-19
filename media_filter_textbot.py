from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# Telegram & Mongo Config
api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
session_string = "BQG2HWgAhXKS3YQN7ItANKtfvPx_jcO23EAvyP5-AKgwP0T5dFJLVO2kOqC_LLeGCHTpWGBfRSr4P4t5QU7Sq7-w5NyZ9tilzveyNz0EOJHp6k_jM9SWP1P2o4Qv_P0k7TCuCD5sWSVYFoRHzjOTEXIWYGuXoyiskH-twdYeFdpiWwAu2xmzAjj6suJvnV-iYSfP_Jf44GSwPxJHKPs2PzH1-TCXoP3GTBuzZocu0jGtZrZwHUAn1xFAq7_9XmAvVqJBJgyTdhAVeFNjJUqD4WFz764GY1JF3EGptIoLw1zYoGgDOPoUxWIYEFPkuNyO3MF3m5q4ehtlOpJHGCw7D1OHpN_pOQAAAAHDNnyBAA"
mongo_url = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
channel_username = "moviestera1"  # without @

# Start Mongo Client
mongo_client = MongoClient(mongo_url)
db = mongo_client["lucas"]
collection = db["Telegram_files"]

# Start Pyrogram client using session string
app = Client(
    name="user_session",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

# Flask health check
web_app = Flask("")

@web_app.route("/")
def home():
    return "Bot is running."

def run():
    web_app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# Telegram command handler
@app.on_message(filters.command("update") & filters.me)
async def update_db(client, message: Message):
    await message.reply("Collecting messages...")

    async for msg in client.get_chat_history(channel_username):
        if not msg.media:
            continue
        if collection.find_one({"message_id": msg.id}):
            continue

        collection.insert_one({
            "message_id": msg.id,
            "text": msg.caption if msg.caption else "",
            "file_name": msg.document.file_name if msg.document else None
        })

    await message.reply("Messages saved successfully.")

# Start bot
app.run()
