from flask import Flask
import feedparser
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

last_sent_hour = None # Global variable to prevent duplicate messages

@app.route("/")
def send_trending():
    global last_sent_hour

    # Use Korea time (UTC+9)
    now = datetime.utcnow() + timedelta(hours=9)
    hour = now.hour
    minute = now.minute

    # Block messages during 23:01–05:59
    if (hour == 23 and minute >= 1) or (0 <= hour < 6):
        return f"Quiet hours — no message sent at {now.strftime('%H:%M')}"

    # Only send message at o'clock and not if already sent this hour
    if minute != 0 or last_sent_hour == hour:
        return f"No message sent — current time: {now.strftime('%H:%M')}"

    TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "Bot token or chat ID not set!"

    # Get KR and US trends
    kr_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=KR')
    us_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=US')

    kr_titles = [f"[{entry.title}]" for entry in kr_feed.entries[:10]]
    us_titles = [f"({entry.title})" for entry in us_feed.entries[:10]]

    # Format message with a blank line between
    message = " ".join(kr_titles) + "\n\n" + " ".join(us_titles)

    # Send Telegram message
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return f"Failed to send: {response.text}"

    last_sent_hour = hour # Update sent hour
    return f"Message sent at {now.strftime('%H:%M')}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)