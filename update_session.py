import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pymongo import MongoClient
from flask import Flask

logging.basicConfig(level=logging.INFO)

api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
session_string = "BQG2HWgAMqvwjVvhBwXHXvpfwILRCGue7x1DktUIqDVZWXsrVJR8aD7dMljcpF8qMyQ7K2yKZtPmNsythsa0UrTuZTyksnAmm2kYx2NxB3dFl5ZWAZdoZBE2886uQuTDqYO4gvSdHL5DsJP-6lbaTX0J9SfSnuThzUjwLozPPfPRGZTAUVlRC6xhSx6uQP-rH-1LsB0f-WCaqrRacZwAxhqRWKDykWWF8I6KYnDER7hCjTnBQpBumWvBj2qmfek_MI-Zbl4fwNPVc7XINK6NPzMLfjJRjWO-cjuZQkWp29NFcbgg8sWt7spCxnumXyRtWeYrsw9EXn5JQsThLmhMtmu_uoCwmQAAAAHDNnyBAA"
mongo_url = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
channel_username = "moviestera1"

client = MongoClient(mongo_url)
db = client["lucas"]
collection = db["Telegram_files"]

app = Client("user_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!", 200

@app.on_message(filters.command("update") & filters.me)
async def update_db(_, message: Message):
    await message.reply("Collecting messages...")
    saved, skipped, errors = 0, 0, 0

    async for msg in app.get_chat_history(channel_username):
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
                "file_name": (msg.caption or "").strip().split("\n")[0],
                "file_link": f"https://t.me/{channel_username}/{msg.id}"
            })
            saved += 1
        except Exception as e:
            logging.error(f"Insert failed for {msg.id}: {e}")
            errors += 1
        await asyncio.sleep(0.2)

    await message.reply(f"Update done.\nSaved: {saved} | Skipped: {skipped} | Errors: {errors}")

@app.on_message(filters.command("fixfiles") & filters.me)
async def fix_files(_, message: Message):
    updated = 0
    for doc in collection.find({"file_name": None}):
        text = doc.get("text", "").strip()
        if text:
            first_line = text.split("\n")[0]
            collection.update_one({"_id": doc["_id"]}, {"$set": {"file_name": first_line}})
            updated += 1
    await message.reply(f"Updated file names for {updated} documents.")

# NEW: Check channel access command
@app.on_message(filters.command("checkchannel") & filters.me)
async def check_channel(_, message: Message):
    try:
        chat = await app.get_chat(channel_username)
        await message.reply(f"Channel Found:\nTitle: {chat.title}\nID: {chat.id}")
    except Exception as e:
        await message.reply(f"Failed to access channel:\n{e}")

async def start_flask():
    import threading
    def run():
        flask_app.run(host="0.0.0.0", port=8080)
    thread = threading.Thread(target=run)
    thread.start()

async def main():
    await app.start()
    await start_flask()
    await idle()
    await app.stop()

if __name__ == '__main__':
    import uvloop
    uvloop.install()
    asyncio.run(main())
