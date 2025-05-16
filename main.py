from flask import Flask
import feedparser
import requests
import os

app = Flask(__name__)

@app.route("/")
def send_trending():
    # Google Trends RSS (Korea)
    RSS_URL = 'https://trends.google.com/trending/rss?geo=KR'
    TELEGRAM_BOT_TOKEN = '7634402374:AAGzwu9D-s_1MLgVWwoKl4WkvD8L1b0rUKA'
    TELEGRAM_CHAT_ID = '8151125156'

    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:10]

    # Format top 10 keywords
    message = "Top 10 Google Trending Searches in Korea:\n"
    for i, entry in enumerate(entries, 1):
        message += f"{i}. {entry.title}\n"

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    requests.post(url, data=payload)

    return "Sent to Telegram!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)