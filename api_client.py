import logging
import httpx
import random
from datetime import date, timedelta
from config import LEAGUES

logger = logging.getLogger(__name__)

BASE = "https://www.thesportsdb.com/api/v1/json/3"


async def _get(url: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"HTTP error: {e}")
        return None


async def get_fixtures_on_date(league_id: str, date_str: str) -> list[dict]:
    data = await _get(f"{BASE}/eventsday.php?d={date_str}&l={league_id}")
    if not data or not data.get("events"):
        return []
    return [e for e in data["events"] if e.get("strSport") == "Soccer"]


async def fetch_all_todays_predictions() -> list[dict]:
    today = date.today().isoformat()
    results = []

    for league_name, meta in LEAGUES.items():
        fixtures = await get_fixtures_on_date(meta["league_id"], today)
        for f in fixtures:
            home = f.get("strHomeTeam", "Home")
            away = f.get("strAwayTeam", "Away")
            kickoff = f.get("strTime", "TBD")
            fixture_id = f.get("idEvent", str(random.randint(100000, 999999)))
            prediction = _generate_prediction(home, away)
            results.append({
                "league": league_name,
                "emoji": meta["emoji"],
                "fixture_id": fixture_id,
                "home": home,
                "away": away,
                "kickoff": kickoff,
                "prediction": prediction,
            })

    return results


async def fetch_upcoming_matches(days: int = 3) -> list[dict]:
    results = []
    today = date.today()

    for league_name, meta in LEAGUES.items():
        for i in range(1, days + 1):
            check_date = (today + timedelta(days=i)).isoformat()
            fixtures = await get_fixtures_on_date(meta["league_id"], check_date)
            for f in fixtures:
                results.append({
                    "league": league_name,
                    "emoji": meta["emoji"],
                    "fixture_id": f.get("idEvent", ""),
                    "home": f.get("strHomeTeam", "Home"),
                    "away": f.get("strAwayTeam", "Away"),
                    "kickoff": f"{check_date} {f.get('strTime', '')}",
                })

    return results


async def get_fixture_result(fixture_id: str) -> dict | None:
    data = await _get(f"{BASE}/lookupevent.php?id={fixture_id}")
    if not data or not data.get("events"):
        return None
    return data["events"][0]


def _generate_prediction(home: str, away: str) -> dict:
    roll = random.random()
    if roll < 0.46:
        winner = home
        advice = f"{home} to win (Home advantage)"
        pct_home, pct_draw, pct_away = _split(55, 22, 23)
    elif roll < 0.72:
        winner = "Draw"
        advice = "Both teams likely to share points"
        pct_home, pct_draw, pct_away = _split(28, 42, 30)
    else:
        winner = away
        advice = f"{away} to win (Strong away form)"
        pct_home, pct_draw, pct_away = _split(22, 23, 55)

    return {
        "winner": winner,
        "advice": advice,
        "percent": {"home": pct_home, "draw": pct_draw, "away": pct_away},
    }


def _split(h: int, d: int, a: int) -> tuple:
    noise = random.randint(-5, 5)
    return f"{h + noise}%", f"{d}%", f"{a - noise}%"
