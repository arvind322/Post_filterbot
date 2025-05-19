from pyrogram import Client, filters
from pymongo import MongoClient
import os

API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAH4G_Qrry4X6EjLR6mpA13elZYxqw6zVIQ"
CHANNEL_USERNAME = "moviestera1"

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["MediaBot"]
collection = db["Messages"]

bot = Client("media_filter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("update"))
async def update_db(client, message):
    user_id = message.from_user.id if message.from_user else None
    member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
    if not (member.status in ("administrator", "creator")):
        return await message.reply("Sirf channel admin hi `/update` command chala sakta hai.")

    await message.reply("Messages collecting started...")
    async for msg in client.get_chat_history(CHANNEL_USERNAME):
        if msg.text:
            post_link = f"https://t.me/{CHANNEL_USERNAME}/{msg.message_id}"
            title = msg.text.splitlines()[0][:100]
            body = msg.text
            filename = f"{title[:50].strip()}.txt"
            collection.update_one(
                {"message_id": msg.message_id},
                {
                    "$set": {
                        "title": title,
                        "body": body,
                        "filename": filename,
                        "link": post_link,
                        "channel": CHANNEL_USERNAME,
                        "message_id": msg.message_id
                    }
                },
                upsert=True
            )
    await message.reply("Done. All text messages saved.")

@bot.on_message(filters.text)
async def search_messages(client, message):
    query = message.text
    results = collection.find({"title": {"$regex": query, "$options": "i"}}).limit(5)
    found = False
    for msg in results:
        reply_text = f"""**{msg['title']}**
Body: {msg['body']}
Link: {msg['link']}"""
        await message.reply(reply_text, quote=True)
        found = True
    if not found:
        await message.reply("Kuch nahi mila.", quote=True)

def start_bot():
    bot.run()
