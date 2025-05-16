# app.py
from flask import Flask
import feedparser
import requests

app = Flask(__name__)

@app.route('/')
def send_trending():
    RSS_URL = 'https://trends.google.com/trending/rss?geo=KR'
    TELEGRAM_BOT_TOKEN = '7634402374:AAGzwu9D-s_1MLgVWwoKl4WkvD8L1b0rUXA'
    TELEGRAM_CHAT_ID = '8151125157'

    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:10]

    message = "Top 10 Trending Searches in Korea:\n"
    for i, entry in enumerate(entries, 1):
        message += f"{i}. {entry.title}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }

    requests.post(url, data=payload)
    return "Sent to Telegram!"