from flask import Flask
from threading import Thread
import asyncio
from media_filter_textbot import bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

async def start_bot():
    await bot.start()
    print("Bot started")
    await asyncio.Event().wait()  # Keep bot running

if __name__ == "__main__":
    Thread(target=run_flask).start()  # Flask in thread
    asyncio.run(start_bot())          # Pyrogram bot in main thread
