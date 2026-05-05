import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start_handler,
    predictions_handler,
    accuracy_handler,
    upcoming_handler,
    leagues_handler,
)
from scheduler import start_scheduler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("predictions", predictions_handler))
    app.add_handler(CommandHandler("accuracy", accuracy_handler))
    app.add_handler(CommandHandler("upcoming", upcoming_handler))
    app.add_handler(CommandHandler("leagues", leagues_handler))

    # Start the daily scheduler in background
    loop = asyncio.get_event_loop()
    loop.create_task(start_scheduler(app))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
