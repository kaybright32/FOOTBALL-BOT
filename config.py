config.py — All configuration and constants.
Uses TheSportsDB (free, no key needed) for match data.
"""

import os

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8605536229:AAHUcdlDQaCQ9VukTBkh70bDPv9qJg6cq88")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5109065860")

# ── Leagues (TheSportsDB league IDs) ─────────────────────────────────────────
LEAGUES = {
    "Premier League":   {"league_id": "4328", "country": "England",  "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "La Liga":          {"league_id": "4335", "country": "Spain",    "emoji": "🇪🇸"},
    "Serie A":          {"league_id": "4332", "country": "Italy",    "emoji": "🇮🇹"},
    "Bundesliga":       {"league_id": "4331", "country": "Germany",  "emoji": "🇩🇪"},
    "Ligue 1":          {"league_id": "4334", "country": "France",   "emoji": "🇫🇷"},
    "Champions League": {"league_id": "4480", "country": "Europe",   "emoji": "🏆"},
    "NPFL":             {"league_id": "4686", "country": "Nigeria",  "emoji": "🇳🇬"},
    "Eredivisie":       {"league_id": "4337", "country": "Netherlands", "emoji": "🇳🇱"},
    "Primeira Liga":    {"league_id": "4344", "country": "Portugal", "emoji": "🇵🇹"},
}

# ── Scheduler ─────────────────────────────────────────────────────────────────
DAILY_PREDICTIONS_HOUR = 7     # 7 AM UTC = 8 AM WAT
DAILY_PREDICTIONS_MINUTE = 0

# ── Storage ───────────────────────────────────────────────────────────────────
DB_PATH = "predictions.db"
