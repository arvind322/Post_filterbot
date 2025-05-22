# --- update_session.py (for /update and /fixfiles with session) ---

import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

api_id = 28712296
api_hash = "25a96a55e729c600c0116f38564a635f"
session_string = "<your_session_string>"
mongo_url = "<your_mongo_url>"
channel_username = "moviestera1"

client = MongoClient(mongo_url)
db = client["lucas"]
collection = db["Telegram_files"]

app = Client("user_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

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

async def main():
    await app.start()
    await idle()

if __name__ == '__main__':
    import uvloop
    uvloop.install()
    asyncio.run(main())
