from flask import Flask
import threading
from media_filter_textbot import bot  # आपका bot जो Pyrogram Client है

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    try:
        bot.run()
    except Exception as e:
        print("Bot error:", e)

if __name__ == "__main__":
    # Pyrogram bot को अलग thread में चलाएं ताकि Flask को block न करे
    threading.Thread(target=run_bot).start()
    # Flask app चलाएं, 0.0.0.0 पर और पोर्ट 8080 पर
    app.run(host="0.0.0.0", port=8080)
