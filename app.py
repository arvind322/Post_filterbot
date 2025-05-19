from flask import Flask
from threading import Thread
import asyncio
from media_filter_textbot import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Media Filter Bot is Running on Koyeb!"

def run_bot():
    async def start():
        await bot.start()
        print("Bot started.")
        while True:
            await asyncio.sleep(10)  # Keeps the bot alive
    asyncio.run(start())

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
