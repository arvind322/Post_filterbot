from pyrogram import Client, filters
from pymongo import MongoClient
from flask import Flask

app = Flask(__name__)

API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["lucas"]
collection = db["Telegram_files"]

@app.route("/")
def home():
    return "Bot is running"

@bot.on_message(filters.private & filters.forwarded & filters.incoming)
async def handle_forwarded_message(client, message):
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
            print(f"Inserted: {file_name} -> {telegram_link}")
        else:
            print(f"Already exists: {file_name} -> {telegram_link}")

if __name__ == "__main__":
    import threading
    import asyncio

    # Run Flask in a separate thread
    def run_flask():
        app.run(host="0.0.0.0", port=8080)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run pyrogram bot (async)
    bot.run()
