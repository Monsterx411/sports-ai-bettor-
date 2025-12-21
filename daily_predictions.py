#!/usr/bin/env python3
"""
Daily predictions runner: generates at least MIN_DAILY_MATCHES recommendations,
saves results to logs/predictions_YYYYMMDD.json, and prints a concise summary.
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings, LOGS_DIR
from src.integrated_prediction import get_prediction_engine


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def serialize_rec(r):
    return {
        "match_id": r.match_id,
        "sport": r.sport,
        "league": r.league,
        "home_team": r.home_team,
        "away_team": r.away_team,
        "predicted_winner": r.predicted_winner,
        "confidence": round(float(r.prediction_confidence or 0), 4),
        "predicted_probability": round(float(r.predicted_probability or 0), 4),
        "market_probability": round(float(r.market_probability or 0), 4),
        "edge": round(float(r.edge or 0), 4),
        "expected_value": round(float(r.expected_value or 0), 4),
        "recommended_odds": float(r.recommended_odds or 0),
        "bookmaker": r.bookmaker,
    }


def main() -> int:
    print("\n=== Daily Predictions Runner ===")
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {date_str}")

    ensure_dir(Path(LOGS_DIR))

    engine = get_prediction_engine()

    # Train (advanced) if desired
    if settings.USE_ADVANCED_TRAINING:
        try:
            print("Training advanced model...")
            engine.train_on_live_and_historical(sport=settings.DEFAULT_SPORT, advanced=True)
            print("Advanced training complete.")
        except Exception as e:
            print(f"Training warning: {e}")

    sports = [s.strip() for s in settings.TOP_SPORTS.split(',') if s.strip()]
    recs = engine.get_daily_predictions(min_matches=settings.MIN_DAILY_MATCHES, sports=sports)

    # Save
    out = {
        "timestamp": today.isoformat(),
        "sports": sports,
        "min_requested": settings.MIN_DAILY_MATCHES,
        "count": len(recs),
        "recommendations": [serialize_rec(r) for r in recs],
    }

    out_path = Path(LOGS_DIR) / f"predictions_{today.strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    # Print summary
    strong = sum(1 for r in recs if r.recommendation == "STRONG_BUY")
    buys = sum(1 for r in recs if r.recommendation == "BUY")
    print(f"Generated {len(recs)} recommendations (Strong: {strong}, Buy: {buys})")
    print(f"Saved to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
