from datetime import datetime
from config import LEAGUES


def predictions_message(matches: list[dict]) -> str:
    if not matches:
        return (
            "⚽ <b>No matches scheduled today</b> across tracked leagues.\n\n"
            "Try /upcoming to see what's coming this week!"
        )

    lines = ["🗓 <b>Today's Match Predictions</b>\n"]
    current_league = None

    for m in matches:
        if m["league"] != current_league:
            current_league = m["league"]
            lines.append(f"\n{m['emoji']} <b>{current_league}</b>")
            lines.append("─" * 28)

        pred = m["prediction"]
        pct = pred["percent"]
        kickoff = m.get("kickoff", "TBD")

        lines.append(
            f"⏰ {kickoff} WAT\n"
            f"🏠 {m['home']}  vs  ✈️ {m['away']}\n"
            f"📊 Home {pct.get('home','?')} | Draw {pct.get('draw','?')} | Away {pct.get('away','?')}\n"
            f"💡 <b>Tip:</b> {pred['advice']}\n"
            f"🏆 <b>Pick:</b> {pred['winner']}\n"
        )

    lines.append("<i>Predictions based on home advantage stats. Bet responsibly.</i>")
    return "\n".join(lines)


def upcoming_message(matches: list[dict]) -> str:
    if not matches:
        return "📅 No upcoming matches found in the next 3 days."

    lines = ["📅 <b>Upcoming Matches (Next 3 Days)</b>\n"]
    current_league = None

    for m in sorted(matches, key=lambda x: x["kickoff"]):
        if m["league"] != current_league:
            current_league = m["league"]
            lines.append(f"\n{m['emoji']} <b>{current_league}</b>")

        kickoff = m.get("kickoff", "TBD")
        lines.append(f"  • {m['home']} vs {m['away']} — {kickoff}")

    return "\n".join(lines)


def accuracy_message(stats: dict) -> str:
    total = stats["total"]
    correct = stats["correct"]
    pending = stats["pending"]
    pct = stats["accuracy_pct"]

    lines = [
        "📈 <b>Prediction Accuracy</b>\n",
        f"Total predictions: <b>{total}</b>",
        f"Correct: <b>{correct}</b>",
        f"Pending results: <b>{pending}</b>",
        f"Accuracy: <b>{pct}%</b>",
        "\n<b>By League:</b>",
    ]

    if stats["by_league"]:
        for lg in stats["by_league"]:
            filled = int(lg["pct"] // 10)
            bar = "🟩" * filled + "⬜" * (10 - filled)
            lines.append(f"  {lg['league']}: {bar} {lg['pct']}% ({lg['correct']}/{lg['total']})")
    else:
        lines.append("  No resolved predictions yet — check back after matches finish!")

    return "\n".join(lines)


def leagues_message(leagues: dict) -> str:
    lines = ["⚽ <b>Tracked Leagues</b>\n"]
    for name, meta in leagues.items():
        lines.append(f"{meta['emoji']} {name} ({meta['country']})")
    lines.append(f"\nTotal: <b>{len(leagues)} leagues</b>")
    return "\n".join(lines)
