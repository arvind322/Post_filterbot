import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient, errors as pymongo_errors
from flask import Flask
from threading import Thread

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Telegram & Mongo Config
api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
session_string = "BQG2HWgAhXKS3YQN7ItANKtfvPx_jcO23EAvyP5-AKgwP0T5dFJLVO2kOqC_LLeGCHTpWGBfRSr4P4t5QU7Sq7-w5NyZ9tilzveyNz0EOJHp6k_jM9SWP1P2o4Qv_P0k7TCuCD5sWSVYFoRHzjOTEXIWYGuXoyiskH-twdYeFdpiWwAu2xmzAjj6suJvnV-iYSfP_Jf44GSwPxJHKPs2PzH1-TCXoP3GTBuzZocu0jGtZrZwHUAn1xFAq7_9XmAvVqJBJgyTdhAVeFNjJUqD4WFz764GY1JF3EGptIoLw1zYoGgDOPoUxWIYEFPkuNyO3MF3m5q4ehtlOpJHGCw7D1OHpN_pOQAAAAHDNnyBAA"
mongo_url = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
channel_username = "moviestera1"

# Mongo Client
try:
    mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    mongo_client.server_info()  # Trigger connection
    db = mongo_client["lucas"]
    collection = db["Telegram_files"]
    logging.info("MongoDB connection established.")
except pymongo_errors.ServerSelectionTimeoutError as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise SystemExit("Exiting due to MongoDB connection failure.")

# Pyrogram client
app = Client(
    name="user_session",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

# Flask for health check
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Bot is running!'

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

# Telegram command handler
@app.on_message(filters.command("update") & filters.me)
async def update_db(client, message: Message):
    await message.reply("Collecting messages...")

    saved = 0
    skipped = 0
    errors = 0

    try:
        async for msg in client.get_chat_history(channel_username):
            if not msg.media:
                skipped += 1
                continue
            if collection.find_one({"message_id": msg.id}):
                skipped += 1
                continue

            try:
                collection.insert_one({
                    "message_id": msg.id,
                    "text": msg.caption or "",
                    "file_name": msg.document.file_name if msg.document else None
                })
                saved += 1
            except pymongo_errors.PyMongoError as e:
                logging.error(f"MongoDB insert failed for message {msg.id}: {e}")
                errors += 1
    except Exception as e:
        logging.exception(f"Failed to fetch messages from @{channel_username}: {e}")
        await message.reply(f"Failed to collect messages: {e}")
        return

    log_msg = f"Saved: {saved} | Skipped: {skipped} | Errors: {errors}"
    logging.info(log_msg)
    await message.reply(f"Update completed.\n{log_msg}")

# Start bot
app.run()
