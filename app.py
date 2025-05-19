from flask import Flask
import threading
import asyncio
from media_filter_textbot import bot
from pyrogram.raw.functions import Ping

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    async def main():
        await bot.connect()
        await bot.invoke(Ping(ping_id=0))  # टाइम सिंक के लिए जरूरी
        await bot.start()
        print("Bot started")
        await asyncio.get_event_loop().create_future()  # bot को चलाता रहे

    asyncio.run(main())

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
