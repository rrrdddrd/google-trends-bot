from flask import Flask
import feedparser
import requests
import os
import re
from datetime import datetime, timedelta

app = Flask(__name__)

last_sent_hour = None  # Global variable to prevent duplicate messages

# Pattern to detect Vietnamese characters
VIETNAMESE_CHAR_PATTERN = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệ"
                                     r"ìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]")

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

    # Parse KR and US feeds
    kr_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=KR')
    us_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=US')

    # Filter KR keywords to exclude Vietnamese, fill in extras if needed
    filtered_kr_titles = []
    for entry in kr_feed.entries:
        if not VIETNAMESE_CHAR_PATTERN.search(entry.title):
            filtered_kr_titles.append(f"[{entry.title}]")
        if len(filtered_kr_titles) == 10:
            break

    # US trends (no filter)
    us_titles = [f"({entry.title})" for entry in us_feed.entries[:10]]

    # Format message
    message = " ".join(filtered_kr_titles) + "\n\n" + " ".join(us_titles)

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return f"Failed to send: {response.text}"

    last_sent_hour = hour  # Prevent sending multiple times in same hour
    return f"Message sent at {now.strftime('%H:%M')}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)