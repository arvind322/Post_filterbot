import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pymongo import MongoClient

# ---------------------------
# 🔧 CONFIG (Your credentials)
API_ID = 28712296
API_HASH = "25a96a55e729c600c0116f38564a635f"
BOT_TOKEN = "7462333733:AAGTipaAqOSqPORNOuwERnEHBQGLoPbXxfE"
MONGO_URI = "mongodb+srv://lucas:00700177@lucas.miigb0j.mongodb.net/?retryWrites=true&w=majority&appName=lucas"

# ---------------------------
# 🌐 Flask Web Server for Koyeb
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ---------------------------
# 🤖 Telegram Bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------------------
# 🍿 MongoDB
client = MongoClient(MONGO_URI)
db = client['movie_db']  # your DB name
collection = db['movies']  # your collection name

# ---------------------------
# 💬 /start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! ✅ I'm alive and running on Koyeb!")

# 🎬 Movie search (group + private)
@bot.on_message(filters.text & ~filters.command(["start"]))
async def search_movie(client, message):
    query = message.text.strip()

    # Search in MongoDB
    result = collection.find_one({
        "title": {"$regex": query, "$options": "i"}
    })

    if result:
        text = (
            f"🎬 *{result.get('title')}*\n"
            f"📅 Year: {result.get('year')}\n"
            f"🔗 Link: {result.get('link')}"
        )
    else:
        # Only send "not found" in private; ignore in group
        if message.chat.type == "private":
            text = "❌ Movie not found in database."
        else:
            return

    await message.reply_text(text, quote=True)

# ---------------------------
bot.run()
