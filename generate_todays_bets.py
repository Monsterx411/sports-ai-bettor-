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
        
        print("\n✅ Loading live sports data fetcher...")
        live_fetcher = LiveSportsDataFetcher()
        
        print("✅ Loading unified data source manager...")
        data_manager = UnifiedDataSourceManager()
        
        print("✅ Loading prediction engine...")
        prediction_engine = IntegratedPredictionEngine()
        
        # Fetch today's soccer matches
        print("\n📊 Fetching today's soccer matches...")
        today_matches = live_fetcher.fetch_live_soccer_matches()
        
        if today_matches:
            print(f"✅ Found {len(today_matches)} soccer matches for today")
            
            # Display upcoming matches
            print("\n" + "-"*80)
            print("📅 TODAY'S UPCOMING MATCHES")
            print("-"*80)
            
            for idx, match in enumerate(today_matches[:10], 1):  # Show first 10
                print(f"\n{idx}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                if match.get('league'):
                    print(f"   League: {match['league']}")
                if match.get('match_date'):
                    print(f"   Time: {match['match_date']}")
                if match.get('odds'):
                    odds = match['odds']
                    print(f"   Odds - Home: {odds.get('home', 'N/A')} | Draw: {odds.get('draw', 'N/A')} | Away: {odds.get('away', 'N/A')}")
        else:
            print("⚠️  No matches found for today. Using mock data for demonstration...")
            today_matches = create_mock_matches()
            print(f"✅ Created {len(today_matches)} mock matches for demonstration")
        
        # Generate predictions
        print("\n" + "-"*80)
        print("🤖 GENERATING PREDICTIONS")
        print("-"*80)
        
        try:
            # Train on historical data
            print("\n📚 Training model on historical data...")
            prediction_engine.train_on_live_and_historical(sport="soccer")
            print("✅ Model training complete")
            
            # Generate predictions for matches
            predictions = []
            for match in today_matches[:5]:  # Predict top 5 matches
                try:
                    pred = prediction_engine.predict_match(
                        home_team=match.get('home_team'),
                        away_team=match.get('away_team'),
                        odds_home=match.get('odds', {}).get('home'),
                        odds_draw=match.get('odds', {}).get('draw'),
                        odds_away=match.get('odds', {}).get('away')
                    )
                    if pred:
                        predictions.append({
                            'match': match,
                            'prediction': pred
                        })
                except Exception as e:
                    print(f"⚠️  Could not predict {match.get('home_team')} vs {match.get('away_team')}: {str(e)[:50]}")
            
            if predictions:
                # Display predictions
                print("\n" + "-"*80)
                print("💰 VALUE BET RECOMMENDATIONS")
                print("-"*80)
                
                for idx, item in enumerate(predictions, 1):
                    match = item['match']
                    pred = item['prediction']
                    
                    print(f"\n{idx}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                    print(f"   League: {match.get('league', 'N/A')}")
                    
                    if isinstance(pred, dict):
                        print(f"   Prediction: {pred.get('prediction', 'N/A')}")
                        if pred.get('confidence'):
                            print(f"   Confidence: {pred['confidence']:.1%}")
                        if pred.get('edge'):
                            edge_pct = (pred['edge'] * 100) if pred['edge'] else 0
                            print(f"   Edge: +{edge_pct:.1f}% (Value Bet)")
                        if pred.get('expected_value'):
                            print(f"   Expected Value: ${pred['expected_value']:.2f} per $1 bet")
                        if pred.get('recommendation'):
                            recommendation = pred['recommendation']
                            emoji = {
                                'STRONG_BUY': '🚀',
                                'BUY': '✅',
                                'HOLD': '⏸️',
                                'SELL': '⚠️',
                                'AVOID': '❌'
                            }.get(recommendation, '•')
                            print(f"   Recommendation: {emoji} {recommendation}")
                
                # Summary statistics
                print("\n" + "-"*80)
                print("📈 SUMMARY")
                print("-"*80)
                strong_buys = sum(1 for p in predictions if p['prediction'].get('recommendation') == 'STRONG_BUY')
                buys = sum(1 for p in predictions if p['prediction'].get('recommendation') == 'BUY')
                
                print(f"✅ Total Predictions Generated: {len(predictions)}")
                print(f"🚀 Strong Buy Opportunities: {strong_buys}")
                print(f"✅ Buy Opportunities: {buys}")
                print(f"💡 Prediction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            else:
                print("⚠️  Could not generate predictions at this time.")
                print("💡 Tip: Make sure API keys are valid in .env file")
                
        except Exception as e:
            print(f"⚠️  Error during prediction: {str(e)}")
            print("💡 This might be due to: invalid API keys, no internet connection, or API limits reached")
        
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
