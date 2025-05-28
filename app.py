# app.py

import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from flask import Flask
import threading

# Logging
logging.basicConfig(level=logging.INFO)

# Configs
api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
bot_token = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
session_string = "BQG2HWgAMqvwjVvhBwXHXvpfwILRCGue7x1DktUIqDVZWXsrVJR8aD7dMljcpF8qMyQ7K2yKZtPmNsythsa0UrTuZTyksnAmm2kYx2NxB3dFl5ZWAZdoZBE2886uQuTDqYO4gvSdHL5DsJP-6lbaTX0J9SfSnuThzUjwLozPPfPRGZTAUVlRC6xhSx6uQP-rH-1LsB0f-WCaqrRacZwAxhqRWKDykWWF8I6KYnDER7hCjTnBQpBumWvBj2qmfek_MI-Zbl4fwNPVc7XINK6NPzMLfjJRjWO-cjuZQkWp29NFcbgg8sWt7spCxnumXyRtWeYrsw9EXn5JQsThLmhMtmu_uoCwmQAAAAHDNnyBAA"
mongo_url = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
channel_username = "moviestera1"

# MongoDB
client = MongoClient(mongo_url)
db = client["lucas"]
collection = db["Telegram_files"]

# Flask setup
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!", 200

# Pyrogram bot client
bot_app = Client("movie_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@bot_app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    count = collection.count_documents({})
    await message.reply_text(
        f"👋 Welcome to Movie Search Bot!\n\n"
        f"📽 Channel: @{channel_username}\n"
        f"🎞 Movies in DB: {count}\n\n"
        f"🔍 Just type the movie name to search."
    )

@bot_app.on_message(filters.text & filters.group & ~filters.command(["start", "update", "fixfiles"]))
async def movie_search(_, message: Message):
    query = message.text.strip().lower()
    results = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(5)
    found = False
    for doc in results:
        msg_id = doc.get("message_id")
        if msg_id:
            try:
                await bot_app.copy_message(message.chat.id, f"@{channel_username}", msg_id, reply_to_message_id=message.id)
                found = True
            except Exception as e:
                logging.error(f"Error copying message {msg_id}: {e}")
    if not found:
        await message.reply("❌ Movie not found.", reply_to_message_id=message.id)

# User client for database updates
user_app = Client("user_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

@user_app.on_message(filters.command("update") & filters.me)
async def update_db(_, message: Message):
    await message.reply("🔄 Collecting messages...")
    saved, skipped, errors = 0, 0, 0

    async for msg in user_app.get_chat_history(channel_username):
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
                "file_link": f"https://t.me/{channel_username}/{msg.id}"
            })
            saved += 1
        except Exception as e:
            logging.error(f"Insert failed for {msg.id}: {e}")
            errors += 1
        await asyncio.sleep(0.1)

    await message.reply(f"✅ Update done.\nSaved: {saved} | Skipped: {skipped} | Errors: {errors}")

@user_app.on_message(filters.command("fixfiles") & filters.me)
async def fix_files(_, message: Message):
    updated = 0
    for doc in collection.find({"file_name": None}):
        text = doc.get("text", "").strip()
        if text:
            first_line = text.split("\n")[0]
            collection.update_one({"_id": doc["_id"]}, {"$set": {"file_name": first_line}})
            updated += 1
    await message.reply(f"🛠 Fixed {updated} file names.")

@user_app.on_message(filters.command("checkchannel") & filters.me)
async def check_channel(_, message: Message):
    try:
        chat = await user_app.get_chat(channel_username)
        await message.reply(f"✅ Channel Found:\nTitle: {chat.title}\nID: {chat.id}")
    except Exception as e:
        await message.reply(f"❌ Failed to access channel:\n{e}")

# Start Flask and Clients
def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

async def main():
    threading.Thread(target=run_flask).start()
    await bot_app.start()
    await user_app.start()
    logging.info("Both clients started. Bot is live.")
    await asyncio.Event().wait()  # Keeps the app running

if __name__ == "__main__":
    import uvloop
    uvloop.install()
    asyncio.run(main())
