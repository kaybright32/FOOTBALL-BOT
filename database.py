import sqlite3
import logging
from datetime import date
from config import DB_PATH

logger = logging.getLogger(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS predictions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id  TEXT UNIQUE,
                date        TEXT,
                league      TEXT,
                home_team   TEXT,
                away_team   TEXT,
                predicted   TEXT,
                advice      TEXT,
                pct_home    TEXT,
                pct_draw    TEXT,
                pct_away    TEXT,
                actual      TEXT,
                correct     INTEGER
            );
        """)
    logger.info("Database initialised.")


def save_prediction(match: dict):
    """Store a prediction. Skips if fixture already saved."""
    pred = match["prediction"]
    with get_conn() as conn:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO predictions
                    (fixture_id, date, league, home_team, away_team,
                     predicted, advice, pct_home, pct_draw, pct_away)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match["fixture_id"],
                date.today().isoformat(),
                match["league"],
                match["home"],
                match["away"],
                pred["winner"],
                pred["advice"],
                pred["percent"].get("home", "?"),
                pred["percent"].get("draw", "?"),
                pred["percent"].get("away", "?"),
            ))
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")


def update_result(fixture_id: str, actual_winner: str, predicted: str):
    """Update a prediction row with the actual match result."""
    correct = 1 if actual_winner.lower() == predicted.lower() else 0
    with get_conn() as conn:
        conn.execute("""
            UPDATE predictions
            SET actual = ?, correct = ?
            WHERE fixture_id = ?
        """, (actual_winner, correct, fixture_id))


def get_accuracy_stats() -> dict:
    """Return overall and per-league accuracy stats."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(correct) as correct,
                SUM(CASE WHEN correct IS NULL THEN 1 ELSE 0 END) as pending
            FROM predictions
        """).fetchone()

        league_rows = conn.execute("""
            SELECT league,
                   COUNT(*) as total,
                   SUM(correct) as correct
            FROM predictions
            WHERE correct IS NOT NULL
            GROUP BY league
        """).fetchall()

    total = row["total"] or 0
    correct = row["correct"] or 0
    pending = row["pending"] or 0
    pct = round((correct / (total - pending)) * 100, 1) if (total - pending) > 0 else 0

    leagues = []
    for lr in league_rows:
        t = lr["total"] or 0
        c = lr["correct"] or 0
        leagues.append({
            "league": lr["league"],
            "total": t,
            "correct": c,
            "pct": round((c / t) * 100, 1) if t > 0 else 0,
        })

    return {
        "total": total,
        "correct": correct,
        "pending": pending,
        "accuracy_pct": pct,
        "by_league": sorted(leagues, key=lambda x: x["pct"], reverse=True),
    }


def get_pending_fixtures() -> list[dict]:
    """Return all predictions that haven't been resolved yet."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT fixture_id, predicted, home_team, away_team, league
            FROM predictions
            WHERE correct IS NULL
        """).fetchall()
    return [dict(r) for r in rows]
