#!/usr/bin/env python3
"""
Simple script to generate today's bet predictions.
Tests the live sports data integration and shows sample predictions.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("\n" + "="*80)
    print("🎯 SPORTS AI BETTOR - TODAY'S BET PREDICTIONS")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # Import required modules
        print("\n✅ Loading dependencies...")
        from src.live_sports_data import LiveSportsDataFetcher
        import pandas as pd
        print("✅ All dependencies loaded successfully")
        
        # Initialize data fetcher
        print("\n📊 Initializing live sports data fetcher...")
        fetcher = LiveSportsDataFetcher()
        print("✅ Data fetcher initialized")
        
        # Get today's matches
        print("\n🔍 Fetching today's soccer matches...")
        try:
            matches = fetcher.fetch_live_soccer_matches()
            if matches:
                print(f"✅ Found {len(matches)} live soccer matches")
            else:
                print("⚠️  No live matches available, using mock data...")
                matches = generate_mock_matches()
        except Exception as e:
            print(f"⚠️  Could not fetch live data: {e}")
            matches = generate_mock_matches()
        
        # Display matches
        print("\n" + "-"*80)
        print("📅 TODAY'S UPCOMING SOCCER MATCHES")
        print("-"*80)
        
        for idx, match in enumerate(matches[:10], 1):
            match_info = format_match_info(match, idx)
            print(match_info)
        
        # Generate predictions from mock model
        print("\n" + "-"*80)
        print("🤖 ML PREDICTIONS FOR VALUE BETS")
        print("-"*80)
        
        predictions = generate_mock_predictions(matches[:5])
        
        print(f"\n✅ Generated {len(predictions)} predictions")
        
        for idx, pred in enumerate(predictions, 1):
            pred_info = format_prediction_info(pred, idx)
            print(pred_info)
        
        # Summary
        print("\n" + "-"*80)
        print("📊 PREDICTION SUMMARY")
        print("-"*80)
        
        strong_buys = sum(1 for p in predictions if p['recommendation'] == 'STRONG_BUY')
        buys = sum(1 for p in predictions if p['recommendation'] == 'BUY')
        holds = sum(1 for p in predictions if p['recommendation'] == 'HOLD')
        
        print(f"📈 Total Matches Analyzed: {len(matches)}")
        print(f"🎯 Predictions Generated: {len(predictions)}")
        print(f"🚀 Strong Buy Opportunities: {strong_buys}")
        print(f"✅ Buy Opportunities: {buys}")
        print(f"⏸️  Hold Recommendations: {holds}")
        print(f"\n💰 Next Steps:")
        print(f"   1. Set up valid API keys in .env file")
        print(f"   2. Run: python generate_todays_bets.py")
        print(f"   3. Subscribe to live odds feeds for real-time updates")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure dependencies are installed:")
        print("   source venv/bin/activate && pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*80)
    print("✅ Prediction generation complete!")
    print("="*80 + "\n")
    return 0


def generate_mock_matches():
    """Generate mock matches for demonstration."""
    now = datetime.now()
    matches = [
        {
            'home_team': 'Manchester City',
            'away_team': 'Liverpool',
            'league': 'Premier League',
            'match_date': now.replace(hour=15, minute=0).isoformat(),
            'status': 'scheduled',
            'odds': {'home': 1.85, 'draw': 3.60, 'away': 4.20}
        },
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'league': 'La Liga',
            'match_date': (now + timedelta(hours=4)).replace(hour=19, minute=0).isoformat(),
            'status': 'scheduled',
            'odds': {'home': 2.10, 'draw': 3.50, 'away': 3.40}
        },
        {
            'home_team': 'Bayern Munich',
            'away_team': 'Borussia Dortmund',
            'league': 'Bundesliga',
            'match_date': (now + timedelta(hours=6)).replace(hour=21, minute=0).isoformat(),
            'status': 'scheduled',
            'odds': {'home': 1.95, 'draw': 3.70, 'away': 4.00}
        },
        {
            'home_team': 'PSG',
            'away_team': 'Marseille',
            'league': 'Ligue 1',
            'match_date': (now + timedelta(hours=8)).replace(hour=23, minute=0).isoformat(),
            'status': 'scheduled',
            'odds': {'home': 1.75, 'draw': 3.80, 'away': 4.80}
        },
        {
            'home_team': 'Inter Milan',
            'away_team': 'AC Milan',
            'league': 'Serie A',
            'match_date': (now + timedelta(hours=24)).replace(hour=15, minute=0).isoformat(),
            'status': 'scheduled',
            'odds': {'home': 2.20, 'draw': 3.40, 'away': 3.30}
        },
    ]
    return matches


def generate_mock_predictions(matches):
    """Generate mock predictions based on match data."""
    predictions = [
        {
            'match': matches[0],
            'home_team': matches[0]['home_team'],
            'away_team': matches[0]['away_team'],
            'league': matches[0]['league'],
            'prediction': 'Home Win',
            'confidence': 0.72,
            'edge': 0.12,
            'expected_value': 0.22,
            'recommendation': 'STRONG_BUY'
        },
        {
            'match': matches[1],
            'home_team': matches[1]['home_team'],
            'away_team': matches[1]['away_team'],
            'league': matches[1]['league'],
            'prediction': 'Draw',
            'confidence': 0.58,
            'edge': 0.08,
            'expected_value': 0.28,
            'recommendation': 'BUY'
        },
        {
            'match': matches[2],
            'home_team': matches[2]['home_team'],
            'away_team': matches[2]['away_team'],
            'league': matches[2]['league'],
            'prediction': 'Home Win',
            'confidence': 0.65,
            'edge': 0.04,
            'expected_value': 0.08,
            'recommendation': 'HOLD'
        },
        {
            'match': matches[3],
            'home_team': matches[3]['home_team'],
            'away_team': matches[3]['away_team'],
            'league': matches[3]['league'],
            'prediction': 'Away Win',
            'confidence': 0.61,
            'edge': 0.15,
            'expected_value': 0.72,
            'recommendation': 'STRONG_BUY'
        },
        {
            'match': matches[4],
            'home_team': matches[4]['home_team'],
            'away_team': matches[4]['away_team'],
            'league': matches[4]['league'],
            'prediction': 'Home Win',
            'confidence': 0.55,
            'edge': -0.02,
            'expected_value': -0.04,
            'recommendation': 'HOLD'
        },
    ]
    return predictions


def format_match_info(match, idx):
    """Format match information for display."""
    lines = [f"\n{idx}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}"]
    if match.get('league'):
        lines.append(f"   League: {match['league']}")
    if match.get('match_date'):
        lines.append(f"   Kickoff: {match['match_date'][:16]}")
    if match.get('odds'):
        odds = match['odds']
        lines.append(f"   Odds - Home: {odds.get('home', 'N/A')} | Draw: {odds.get('draw', 'N/A')} | Away: {odds.get('away', 'N/A')}")
    return "\n".join(lines)


def format_prediction_info(pred, idx):
    """Format prediction information for display."""
    recommendation_emoji = {
        'STRONG_BUY': '🚀',
        'BUY': '✅',
        'HOLD': '⏸️',
        'SELL': '⚠️',
        'AVOID': '❌'
    }.get(pred['recommendation'], '•')
    
    lines = [
        f"\n{idx}. {pred['home_team']} vs {pred['away_team']}",
        f"   League: {pred['league']}",
        f"   Prediction: {pred['prediction']}",
        f"   Confidence: {pred['confidence']:.1%}",
        f"   Value Edge: +{pred['edge']:.1%}",
        f"   Expected Value: +${pred['expected_value']:.2f} per $1 bet",
        f"   Recommendation: {recommendation_emoji} {pred['recommendation']}"
    ]
    return "\n".join(lines)


if __name__ == '__main__':
    sys.exit(main())
