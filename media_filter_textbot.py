from pyrogram import Client, filters
from pymongo import MongoClient
import os

# MongoDB Config
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"
client = MongoClient(MONGO_URI)
db = client.lucas
collection = db.movies

# Telegram Config
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
SESSION_STRING = "BQG2HWgAhXKS3YQN7ItANKtfvPx_jcO23EAvyP5-AKgwP0T5dFJLVO2kOqC_LLeGCHTpWGBfRSr4P4t5QU7Sq7-w5NyZ9tilzveyNz0EOJHp6k_jM9SWP1P2o4Qv_P0k7TCuCD5sWSVYFoRHzjOTEXIWYGuXoyiskH-twdYeFdpiWwAu2xmzAjj6suJvnV-iYSfP_Jf44GSwPxJHKPs2PzH1-TCXoP3GTBuzZocu0jGtZrZwHUAn1xFAq7_9XmAvVqJBJgyTdhAVeFNjJUqD4WFz764GY1JF3EGptIoLw1zYoGgDOPoUxWIYEFPkuNyO3MF3m5q4ehtlOpJHGCw7D1OHpN_pOQAAAAHDNnyBAA"
CHANNEL_USERNAME = "moviestera1"  # Without @

app = Client("scraper", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("update"))
async def update_db(client, message):
    await message.reply("Messages collecting started...")

    async for msg in client.get_chat_history(CHANNEL_USERNAME, limit=300):
        if msg.text and not collection.find_one({"message_id": msg.id}):
            collection.insert_one({
                "message_id": msg.id,
                "text": msg.text,
                "date": msg.date,
                "from_channel": CHANNEL_USERNAME
            })
    await message.reply("Messages saved successfully.")

@app.on_message(filters.command("search"))
async def search_movie(client, message):
    query = message.text.split(None, 1)
    if len(query) < 2:
        await message.reply("Please provide a search keyword.")
        return

    keyword = query[1]
    results = collection.find({"text": {"$regex": keyword, "$options": "i"}})
    text = ""

    for doc in results:
        text += f"{doc['text'][:400]}\n\n"  # Only show preview

    await message.reply(text or "No matching results found.")

app.run()
