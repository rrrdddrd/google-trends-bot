from flask import Flask
import feedparser
import requests
import os
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# Pattern to detect Vietnamese characters
VIETNAMESE_CHAR_PATTERN = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệ"
                                     r"ìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]")

@app.route("/")
def send_trending():
    # Korea Standard Time (UTC+9)
    now = datetime.utcnow() + timedelta(hours=9)
    hour = now.hour
    minute = now.minute

    # Block between 23:01 and 05:59
    if (hour == 23 and minute >= 1) or (0 <= hour < 6):
        return f"Quiet hours — no message sent at {now.strftime('%H:%M')}"

    # Only send at exact hour
    if minute != 0:
        return f"Not on the hour — current time: {now.strftime('%H:%M')}"

    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "Bot token or chat ID not set!"

    # Parse both feeds
    kr_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=KR')
    us_feed = feedparser.parse('https://trends.google.com/trending/rss?geo=US')

    # Filter and fill KR trends up to 10
    filtered_kr_titles = []
    for entry in kr_feed.entries:
        if not VIETNAMESE_CHAR_PATTERN.search(entry.title):
            filtered_kr_titles.append(f"[{entry.title}]")
        if len(filtered_kr_titles) == 10:
            break

    # US trends (no filter)
    us_titles = [f"({entry.title})" for entry in us_feed.entries[:10]]

    # Compose message
    message = " ".join(filtered_kr_titles) + "\n\n" + " ".join(us_titles)

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return f"Failed to send: {response.text}"

    return f"Message sent at {now.strftime('%H:%M')}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)