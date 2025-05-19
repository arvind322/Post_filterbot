from flask import Flask
import threading
from media_filter_textbot import bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    bot.run()  # Handles start, connection, and event loop

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
