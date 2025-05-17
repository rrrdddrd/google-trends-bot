import time
from datetime import datetime, timedelta
import feedparser
import requests
import os

TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')
RSS_URL = 'https://trends.google.com/trending/rss?geo=KR'

def send_trending():
    now = datetime.utcnow() + timedelta(hours=9)  # Korea Time
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:10]

    message = f"Top 10 Google Trending Searches in Korea ({now.strftime('%H:%M')}):\n"
    for i, entry in enumerate(entries, 1):
        message += f"{i}. {entry.title}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    print(f"Sent at {now.strftime('%H:%M')}: {response.status_code}")

def wait_until_next_hour():
    now = datetime.utcnow() + timedelta(hours=9)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    wait_seconds = (next_hour - now).total_seconds()
    print(f"Waiting {int(wait_seconds)} seconds until {next_hour.strftime('%H:%M')}")
    time.sleep(wait_seconds)

if __name__ == "__main__":
    while True:
        wait_until_next_hour()
        send_trending()