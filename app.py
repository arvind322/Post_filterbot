from flask import Flask
from threading import Thread
from media_filter_textbot import bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    bot.run()  # This handles event loop correctly and runs forever

if __name__ == "__main__":
    Thread(target=run_flask).start()  # Run Flask on a separate thread
    run_bot()                         # Run bot in main thread (no asyncio.run)
