from flask import Flask
import feedparser
import requests
import os

app = Flask(__name__)

@app.route("/")
def send_trending():
    RSS_URL = 'https://trends.google.com/trending/rss?geo=KR'
    TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "Bot token or chat ID not set!"

    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:10]

    message = "Top 10 Google Trending Searches in Korea:\n"
    for i, entry in enumerate(entries, 1):
        message += f"{i}. {entry.title}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return f"Failed to send message: {response.text}"

    return "Sent to Telegram!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)