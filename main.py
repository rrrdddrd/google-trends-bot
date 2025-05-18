from flask import Flask
from datetime import datetime, timedelta
import feedparser
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def is_on_the_hour():
    now = datetime.utcnow() + timedelta(hours=9)  # Korea time
    return now.minute == 0

def is_allowed_hour():
    now = datetime.utcnow() + timedelta(hours=9)  # Korea time
    return 6 <= now.hour <= 22  # From 06:00 to 22:59

def send_trending():
    # Korea trends
    kr_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=KR')
    kr_titles = [f"[{entry.title}]" for entry in kr_feed.entries[:10]]

    # U.S. trends
    us_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=US')
    us_titles = [f"({entry.title})" for entry in us_feed.entries[:10]]

    # Build message
    message = " ".join(kr_titles) + "\n" + " ".join(us_titles)

    # Send Telegram message
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    print(f"Sent: {response.status_code}")
    return response.status_code

@app.route("/")
def index():
    if is_on_the_hour() and is_allowed_hour():
        send_trending()
        return "Message sent."
    else:
        return "Not time to send message."

if __name__ == "__main__":
    app.run()