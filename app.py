import logging
import asyncio
import threading
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from flask import Flask

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
SESSION_STRING = "BQG2HWgAMqvwjVvhBwXHXvpfwILRCGue7x1DktUIqDVZWXsrVJR8aD7dMljcpF8qMyQ7K2yKZtPmNsythsa0UrTuZTyksnAmm2kYx2NxB3dFl5ZWAZdoZBE2886uQuTDqYO4gvSdHL5DsJP-6lbaTX0J9SfSnuThzUjwLozPPfPRGZTAUVlRC6xhSx6uQP-rH-1LsB0f-WCaqrRacZwAxhqRWKDykWWF8I6KYnDER7hCjTnBQpBumWvBj2qmfek_MI-Zbl4fwNPVc7XINK6NPzMLfjJRjWO-cjuZQkWp29NFcbgg8sWt7spCxnumXyRtWeYrsw9EXn5JQsThLmhMtmu_uoCwmQAAAAHDNnyBAA"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
CHANNEL_ID = -1002479279470
CHANNEL_USERNAME = "moviestera1"  # Set your actual channel username

# --- MongoDB ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["lucas"]
collection = db["Telegram_files"]

# --- Flask App for Render Health Check ---
flask_app = Flask(__name__)
@flask_app.route("/")
def home():
    return "Bot is running!", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# --- Pyrogram Clients ---
bot_app = Client("movie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- Handlers ---

# /start command for bot
@bot_app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    logging.info(f"➡️ /start command received from: {message.from_user.id}")
    count = collection.count_documents({})
    await message.reply_text(
        f"👋 Welcome to Movie Search Bot!\n\n"
        f"📽 Channel: @{CHANNEL_USERNAME}\n"
        f"🎞 Movies in DB: {count}\n\n"
        f"🔍 Just type the movie name to search."
    )

# Movie search for groups
@bot_app.on_message(filters.text & filters.group & ~filters.command(["start", "update", "fixfiles", "checkchannel"]))
async def movie_search(_, message: Message):
    logging.info(f"🔍 Search query received in group {message.chat.id}: {message.text}")
    query = message.text.strip().lower()
    results = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(5)
    found = False
    for doc in results:
        try:
            await bot_app.copy_message(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=doc["message_id"],
                reply_to_message_id=message.id
            )
            found = True
        except Exception as e:
            logging.error(f"❌ Failed to copy message {doc['message_id']}: {e}")
    if not found:
        await message.reply("❌ Movie not found.", reply_to_message_id=message.id)

# /update command for user session
@user_app.on_message(filters.command("update") & filters.me)
async def update_db(_, message: Message):
    logging.info("📥 /update command received from user.")
    await message.reply("🔄 Collecting messages...")
    saved, skipped, errors = 0, 0, 0

    async for msg in user_app.get_chat_history(CHANNEL_ID):
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
                "file_name": (msg.caption or "").split("\n")[0],
                "file_link": f"https://t.me/{CHANNEL_USERNAME}/{msg.id}"
            })
            saved += 1
        except Exception as e:
            logging.error(f"Insert failed for {msg.id}: {e}")
            errors += 1
        await asyncio.sleep(0.1)

    await message.reply(f"✅ Update done.\nSaved: {saved} | Skipped: {skipped} | Errors: {errors}")
    logging.info(f"✅ Update completed. Saved: {saved}, Skipped: {skipped}, Errors: {errors}")

# /fixfiles to update missing file names
@user_app.on_message(filters.command("fixfiles") & filters.me)
async def fix_files(_, message: Message):
    logging.info("🛠 /fixfiles command received from user.")
    updated = 0
    for doc in collection.find({"file_name": None}):
        text = doc.get("text", "").strip()
        if text:
            first_line = text.split("\n")[0]
            collection.update_one({"_id": doc["_id"]}, {"$set": {"file_name": first_line}})
            updated += 1
    await message.reply(f"🛠 Fixed {updated} file names.")
    logging.info(f"🛠 Fixfiles done: {updated} updated")

# /checkchannel to validate access
@user_app.on_message(filters.command("checkchannel") & filters.me)
async def check_channel(_, message: Message):
    logging.info("🔎 /checkchannel command received.")
    try:
        chat = await user_app.get_chat(CHANNEL_ID)
        await message.reply(f"✅ Channel Found:\nTitle: {chat.title}\nID: {chat.id}")
        logging.info(f"✅ Channel accessible: {chat.title} ({chat.id})")
    except Exception as e:
        logging.error(f"❌ Failed to access channel: {e}")
        await message.reply(f"❌ Failed to access channel:\n{e}")


# --- Main Runner ---
async def main():
    # Start Flask server in a separate thread
    threading.Thread(target=run_flask).start()

    # Start both Pyrogram clients
    await bot_app.start()
    await user_app.start()

    logging.info("✅ Both bot and user sessions started and running.")

    # Keep the bot alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    import uvloop
    uvloop.install()  # Use uvloop for better performance
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🚪 Exiting bot...")
