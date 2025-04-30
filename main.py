import asyncio
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
import time
import threading
from random import choice
import os

# Configure logging to file and console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),  # Save logs to bot.log
        logging.StreamHandler()  # Print to console
    ]
)
logger = logging.getLogger(__name__)

# Telegram bot token and chat ID (loaded from environment variables)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7634402374:AAGzwu9D-s_1MLgVWwoKl4WkvD8L1b0rUXA")  # Fixed token
CHAT_ID = os.getenv("CHAT_ID", "8151125157")  # Fallback if env var not set

# Rotate User-Agent to avoid blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
]

async def get_google_trends() -> list:
    """Scrape top 10 trending topics from getdaytrends.com for the US."""
    url = "https://getdaytrends.com/united-states/"
    headers = {"User-Agent": choice(USER_AGENTS)}
    logger.info("Fetching Google Trends via scraping...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch page. Status code: {response.status_code}")
            return [f"Failed to fetch page: {response.status_code}"]

        soup = BeautifulSoup(response.text, "html.parser")
        trend_elements = soup.select("table tbody tr td a")[:10]
        trends = [element.text.strip() for element in trend_elements]

        if not trends:
            logger.warning("No trends found or parsing failed.")
            return ["No trends found at this moment."]

        logger.info(f"Fetched {len(trends)} trends.")
        return trends

    except requests.RequestException as e:
        logger.error(f"Network error fetching trends: {e}")
        return [f"Network error: {str(e)}"]
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return [f"Error fetching trends: {str(e)}"]

async def send_trends() -> None:
    """Fetches and sends the Google Trends list."""
    logger.info("Sending trends...")
    try:
        bot = Bot(token=BOT_TOKEN)
        trends = await get_google_trends()

        if trends and trends[0] != "No trends found at this moment." and not trends[0].startswith("Error"):
            message = "Top 10 Google Trends:\n\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(trends)])
            logger.info("Prepared trends message.")
        else:
            message = trends[0] if trends and len(trends) == 1 else "Could not fetch trends."
            logger.warning(f"Prepared message: {message}")

        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info(f"Message sent to chat ID: {CHAT_ID}")

    except TelegramError as e:
        logger.error(f"Telegram error sending message: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

def run_scheduler():
    """Run the scheduler to send trends every hour with retry logic."""
    while True:
        try:
            asyncio.run(send_trends())
        except Exception as e:
            logger.error(f"Scheduler error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait before retrying
        time.sleep(3600)  # Wait 1 hour between runs

if __name__ == "__main__":
    logger.info("Starting the bot...")
    try:
        import requests
        import bs4
        import telegram
    except ImportError:
        logger.info("Installing required packages...")
        import os
        os.system("pip install requests beautifulsoup4 python-telegram-bot==13.7")

    # Start scheduler in a background thread
    threading.Thread(target=run_scheduler, daemon=True).start()

    # Send trends immediately for testing
    asyncio.run(send_trends())

    # Keep script running
    while True:
        time.sleep(60)
