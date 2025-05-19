from flask import Flask
import threading
import asyncio
from media_filter_textbot import bot  # आपका Pyrogram bot instance

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    asyncio.run(bot.start())  # Bot start करें
    print("Bot started")
    asyncio.get_event_loop().run_forever()  # Event loop को चलाते रहें

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()  # Bot को अलग थ्रेड में चलाएं
    app.run(host="0.0.0.0", port=8080)       # Flask app को मेन थ्रेड में चलाएं
