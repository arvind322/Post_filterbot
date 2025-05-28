from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import asyncio

API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
CHANNEL_USERNAME = "@moviestera1"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

app = Client("movie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["movie_bot"]
movies_col = db["movies"]

async def fetch_and_store_posts():
    async with app:
        try:
            chat = await app.get_chat(CHANNEL_USERNAME)
            async for msg in app.get_chat_history(chat.id, limit=200):
                if msg.text or msg.caption:
                    title = msg.text or msg.caption
                    if not movies_col.find_one({"message_id": msg.id}):
                        movies_col.insert_one({
                            "message_id": msg.id,
                            "title": title,
                            "link": f"https://t.me/{chat.username}/{msg.id}"
                        })
        except Exception as e:
            print(f"Error: {e}")

@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply("Welcome to Movie Bot!\nUse `/search movie name` to find a movie.", quote=True)

@app.on_message(filters.command("search"))
async def search_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: `/search movie name`", quote=True)

    results = movies_col.find({"title": {"$regex": query, "$options": "i"}}).limit(5)
    text = ""
    for result in results:
        text += f"• [{result['title']}]({result['link']})\n"

    if text:
        await message.reply(text, disable_web_page_preview=True, quote=True)
    else:
        await message.reply("No results found.", quote=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_and_store_posts())
    app.run()
