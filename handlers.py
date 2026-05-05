import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from api_client import fetch_all_todays_predictions, fetch_upcoming_matches
from database import save_prediction, get_accuracy_stats
from formatter import predictions_message, upcoming_message, accuracy_message, leagues_message
from config import LEAGUES

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Welcome to the Football Prediction Bot!</b>\n\n"
        "Here's what I can do:\n\n"
        "📋 /predictions — Today's match predictions\n"
        "📅 /upcoming — Matches in the next 3 days\n"
        "📈 /accuracy — Track prediction accuracy\n"
        "🌍 /leagues — See all tracked leagues\n\n"
        "I also send <b>daily predictions automatically</b> every morning at 7 AM UTC (8 AM WAT).\n\n"
        "<i>Good luck! ⚽</i>"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def predictions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching today's predictions, please wait...")
    matches = await fetch_all_todays_predictions()

    for m in matches:
        save_prediction(m)

    msg = predictions_message(matches)
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def upcoming_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching upcoming matches...")
    matches = await fetch_upcoming_matches(days=3)
    msg = upcoming_message(matches)
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def accuracy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_accuracy_stats()
    msg = accuracy_message(stats)
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def leagues_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = leagues_message(LEAGUES)
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
