
from flask import Flask
import threading
from media_filter_textbot import start_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Media Filter Bot is Running on Koyeb!"

def run():
    start_bot()

if __name__ == "__main__":
    threading.Thread(target=run).start()
    app.run(host="0.0.0.0", port=8080)
