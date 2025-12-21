#!/usr/bin/env python3
"""
Generate today's bet predictions using live data integration.
This script demonstrates the full workflow: fetch live matches, 
generate predictions, and identify value bets.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("\n" + "="*80)
    print("🎯 SPORTS AI BETTOR - TODAY'S BET PREDICTIONS")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # Import the modules
        from live_sports_data import LiveSportsDataFetcher
        from unified_data_source import UnifiedDataSourceManager
        from integrated_prediction import IntegratedPredictionEngine
        
        print("✅ Loading live sports data fetcher...")
        live_fetcher = LiveSportsDataFetcher()

        print("✅ Loading unified data source manager...")
        data_manager = UnifiedDataSourceManager()

        print("✅ Loading prediction engine...")
        prediction_engine = IntegratedPredictionEngine()
        
        # Train model with advanced pipeline
        print("\n📚 Training model (advanced)...")
        try:
            prediction_engine.train_on_live_and_historical(sport="soccer", advanced=True)
            print("✅ Advanced training complete")
        except Exception as e:
            print(f"⚠️  Training warning: {e}")

        # Generate at least 10 predictions across top sports
        print("\n📊 Generating today's predictions (min 10)...")
        from config.settings import settings
        sports = [s.strip() for s in settings.TOP_SPORTS.split(",") if s.strip()]
        predictions = prediction_engine.get_daily_predictions(min_matches=settings.MIN_DAILY_MATCHES, sports=sports)
        
        if predictions:
            # Display predictions
            print("\n" + "-"*80)
            print("💰 TODAY'S BET RECOMMENDATIONS (Top 10)")
            print("-"*80)

            for idx, rec in enumerate(predictions, 1):
                print(f"\n{idx}. {rec.home_team} vs {rec.away_team} [{rec.sport}]")
                print(f"   Predicted: {rec.predicted_winner}")
                print(f"   Confidence: {rec.prediction_confidence:.1%}")
                print(f"   Edge: {rec.edge:.1%}")
                print(f"   Recommendation: {rec.recommendation}")
        else:
            print("⚠️  Could not generate predictions at this time.")
            print("💡 Tip: Provide valid API keys in .env for live odds and matches")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've run: source venv/bin/activate && pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*80)
    print("✅ Bet prediction generation complete!")
    print("="*80 + "\n")
    return 0


def create_mock_matches():
    """Create mock matches for demonstration when no live data is available."""
    return [
        {
            'home_team': 'Manchester City',
            'away_team': 'Liverpool',
            'league': 'Premier League',
            'match_date': (datetime.now() + timedelta(hours=2)).isoformat(),
            'odds': {'home': 1.85, 'draw': 3.60, 'away': 4.20}
        },
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'league': 'La Liga',
            'match_date': (datetime.now() + timedelta(hours=4)).isoformat(),
            'odds': {'home': 2.10, 'draw': 3.50, 'away': 3.40}
        },
        {
            'home_team': 'Bayern Munich',
            'away_team': 'Borussia Dortmund',
            'league': 'Bundesliga',
            'match_date': (datetime.now() + timedelta(hours=6)).isoformat(),
            'odds': {'home': 1.95, 'draw': 3.70, 'away': 4.00}
        },
        {
            'home_team': 'PSG',
            'away_team': 'Marseille',
            'league': 'Ligue 1',
            'match_date': (datetime.now() + timedelta(hours=8)).isoformat(),
            'odds': {'home': 1.75, 'draw': 3.80, 'away': 4.80}
        },
        {
            'home_team': 'Inter Milan',
            'away_team': 'AC Milan',
            'league': 'Serie A',
            'match_date': (datetime.now() + timedelta(hours=10)).isoformat(),
            'odds': {'home': 2.20, 'draw': 3.40, 'away': 3.30}
        },
    ]


if __name__ == '__main__':
    sys.exit(main())
