import asyncio
import logging
from datetime import datetime, timezone, timedelta
from telegram.constants import ParseMode

from api_client import fetch_all_todays_predictions, get_fixture_result
from database import save_prediction, get_pending_fixtures, update_result
from formatter import predictions_message
from config import (
    TELEGRAM_CHAT_ID,
    DAILY_PREDICTIONS_HOUR,
    DAILY_PREDICTIONS_MINUTE,
)

logger = logging.getLogger(__name__)


def _seconds_until(hour: int, minute: int) -> float:
    """Seconds until next occurrence of HH:MM UTC."""
    now = datetime.now(timezone.utc)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def send_daily_predictions(app):
    """Fetch predictions and push to the configured chat."""
    logger.info("Sending daily predictions...")
    try:
        matches = await fetch_all_todays_predictions()
        for m in matches:
            save_prediction(m)
        msg = predictions_message(matches)
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"Sent predictions for {len(matches)} matches.")
    except Exception as e:
        logger.error(f"Error sending daily predictions: {e}")


async def resolve_pending_results(app):
    """Check all unresolved predictions and update with actual results."""
    pending = get_pending_fixtures()
    if not pending:
        return

    logger.info(f"Resolving {len(pending)} pending fixtures...")
    resolved = []

    for fixture in pending:
        result = await get_fixture_result(fixture["fixture_id"])
        if not result:
            continue

        int_score = result.get("intHomeScore"), result.get("intAwayScore")
        if not int_score[0] or not int_score[1]:
            continue

        home_goals = int(int_score[0])
        away_goals = int(int_score[1])

        if home_goals > away_goals:
            actual = result.get("strHomeTeam", "Home")
        elif away_goals > home_goals:
            actual = result.get("strAwayTeam", "Away")
        else:
            actual = "Draw"

        update_result(fixture["fixture_id"], actual, fixture["predicted"])
        resolved.append(
            f"{'✅' if actual == fixture['predicted'] else '❌'} "
            f"{fixture['home_team']} vs {fixture['away_team']}: "
            f"Predicted <b>{fixture['predicted']}</b>, Actual <b>{actual}</b>"
        )

    if resolved:
        summary = "📊 <b>Result Update</b>\n\n" + "\n".join(resolved)
        try:
            await app.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=summary,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Error sending result update: {e}")


async def start_scheduler(app):
    """Main scheduler loop — runs both daily tasks."""
    from database import init_db
    init_db()

    logger.info("Scheduler started.")

    async def result_loop():
        while True:
            await asyncio.sleep(3 * 3600)
            await resolve_pending_results(app)

    asyncio.create_task(result_loop())

    while True:
        sleep_secs = _seconds_until(DAILY_PREDICTIONS_HOUR, DAILY_PREDICTIONS_MINUTE)
        logger.info(f"Next predictions in {sleep_secs/3600:.1f} hours.")
        await asyncio.sleep(sleep_secs)
        await send_daily_predictions(app)
