import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
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

# /start command handler
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    total = collection.count_documents({})
    await message.reply_text(
        f"**Bot is Alive!**\n\n"
        f"Channel: @{channel_username}\n"
        f"Stored posts in DB: {total}\n\n"
        "Use /update to fetch and save latest posts from your channel."
    )

# /update command
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

            await asyncio.sleep(0.2)

    except FloodWait as e:
        logging.warning(f"FloodWait: Sleeping for {e.value} seconds.")
        await asyncio.sleep(e.value)
        return await update_db(client, message)
    except ConnectionResetError as e:
        logging.warning("ConnectionResetError: retrying in 5 seconds.")
        await asyncio.sleep(5)
        return await update_db(client, message)
    except RPCError as e:
        logging.warning(f"RPCError: {e}. Retrying in 5 seconds.")
        await asyncio.sleep(5)
        return await update_db(client, message)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        await message.reply(f"Failed to collect messages: {e}")
        return

    log_msg = f"Saved: {saved} | Skipped: {skipped} | Errors: {errors}"
    logging.info(log_msg)
    await message.reply(f"Update completed.\n{log_msg}")
# Add this function before app.run()
async def fix_missing_filenames():
    count = 0
    for doc in collection.find({"file_name": None}):
        message_id = doc.get("message_id")
        text = doc.get("text", "")
        if not message_id or not text:
            continue
        first_line = text.strip().split("\n")[0]
        try:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"file_name": first_line}}
            )
            count += 1
        except Exception as e:
            logging.error(f"Failed to update file_name for message {message_id}: {e}")
    logging.info(f"Updated file_name for {count} documents.")

# Start bot
@app.on_message(filters.command("fixfiles") & filters.me)
async def fix_files_command(client, message: Message):
    await message.reply("Fixing file names...")
    await fix_missing_filenames()
    await message.reply("File names updated.")

# Run on startup
async def start_bot():
    await app.start()
    await fix_missing_filenames()  # Auto-fix on startup
    logging.info("Bot started and file names fixed.")
    await idle()

if __name__ == "__main__":
    import uvloop
    from pyrogram.idle import idle
    uvloop.install()
    asyncio.get_event_loop().run_until_complete(start_bot())
# Start bot
