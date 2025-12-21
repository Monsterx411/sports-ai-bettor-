"""
Live Sports Data Integration - Example Usage
Demonstrates how to use live API data with the ML prediction engine
"""

import logging
from datetime import datetime

from src.integrated_prediction import get_prediction_engine
from src.unified_data_source import get_unified_data_manager
from src.live_sports_data import get_live_fetcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_fetch_live_matches():
    """Example 1: Fetch live soccer matches from APIs."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Fetching Live Soccer Matches")
    print("="*60)
    
    fetcher = get_live_fetcher()
    
    # Fetch upcoming Premier League matches
    matches_df = fetcher.fetch_live_soccer_matches(
        league="premier_league",
        days_ahead=7
    )
    
    print(f"\n✅ Found {len(matches_df)} upcoming matches:")
    print(matches_df[['home_team', 'away_team', 'match_time', 'status', 'bookmaker']].head(10))


def example_2_combine_data_sources():
    """Example 2: Train model using combined historical + live data."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Combining Historical and Live Data Sources")
    print("="*60)
    
    data_manager = get_unified_data_manager()
    
    # Get combined training data
    df = data_manager.get_training_data(
        source="combined",
        sport="soccer",
        date_range=("2023-01-01", "2024-12-21")
    )
    
    print(f"\n✅ Combined dataset size: {len(df)} records")
    print(f"   - Date range: {df['match_time'].min()} to {df['match_time'].max()}")
    print(f"   - Columns: {list(df.columns)}")


def example_3_extract_match_features():
    """Example 3: Extract features for specific teams."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extracting Match Features from Historical Data")
    print("="*60)
    
    data_manager = get_unified_data_manager()
    
    # Get features for a specific matchup
    features = data_manager.get_match_features(
        home_team="Manchester City",
        away_team="Liverpool",
        sport="soccer",
        lookback_days=365
    )
    
    if features:
        print("\n✅ Extracted features for Manchester City vs Liverpool:")
        for feature_name, value in features.items():
            print(f"   - {feature_name}: {value:.2f}")
    else:
        print("\n⚠️  Could not extract features (teams may not exist in data)")


def example_4_generate_predictions():
    """Example 4: Generate ML predictions using live data."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Generating ML Predictions")
    print("="*60)
    
    engine = get_prediction_engine()
    
    # Train model on combined data
    print("\nTraining model on combined data...")
    metrics = engine.train_on_live_and_historical(sport="soccer")
    
    if metrics:
        print(f"✅ Model trained!")
        for metric_name, value in metrics.items():
            print(f"   - {metric_name}: {value:.4f}")
    else:
        print("⚠️  Training failed - check data availability")


def example_5_find_value_bets():
    """Example 5: Find best value bets from live matches."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Finding Value Bets")
    print("="*60)
    
    engine = get_prediction_engine()
    
    # Get best value bets for upcoming matches
    print("\nAnalyzing upcoming matches for value opportunities...")
    value_bets = engine.get_best_value_bets(sport="soccer", top_n=5)
    
    if value_bets:
        print(f"\n✅ Found {len(value_bets)} value bets:\n")
        for i, bet in enumerate(value_bets, 1):
            print(f"{i}. {bet.home_team} vs {bet.away_team}")
            print(f"   Recommendation: {bet.recommendation}")
            print(f"   Predicted Winner: {bet.predicted_winner}")
            print(f"   Edge: {bet.edge:.2%}")
            print(f"   Expected Value: {bet.expected_value:.2f}x")
            print(f"   Live Odds: {bet.live_odds_home or bet.live_odds_away:.2f}")
            print(f"   Confidence: {bet.prediction_confidence:.2%}")
            print()
    else:
        print("⚠️  No value bets found")


def example_6_generate_report():
    """Example 6: Generate comprehensive betting analysis report."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Generate Analysis Report")
    print("="*60)
    
    engine = get_prediction_engine()
    
    # Generate analysis report
    print("\nGenerating analysis report...")
    report = engine.generate_report(sport="soccer")
    
    print(f"\n✅ Analysis Report - {report.get('timestamp')}")
    print(f"   Sport: {report.get('sport')}")
    print(f"   Total Matches Analyzed: {report.get('total_matches_analyzed')}")
    print(f"   Positive Edge Bets: {report.get('positive_edge_bets')}")
    print(f"   Average Edge: {report.get('average_edge'):.2%}")
    print(f"   Average Confidence: {report.get('average_confidence'):.2%}")
    
    if report.get('best_value_bets'):
        print(f"\n   Top Value Bets:")
        for bet in report['best_value_bets']:
            print(f"      - {bet['match']}: {bet['recommendation']} (Edge: {bet['edge']})")


def example_7_multi_sport_analysis():
    """Example 7: Analyze multiple sports at once."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Multi-Sport Analysis")
    print("="*60)
    
    fetcher = get_live_fetcher()
    
    # Fetch multiple sports
    print("\nFetching live matches across multiple sports...")
    
    all_matches_df = fetcher.fetch_all_live_matches(
        sports=["soccer", "basketball"],
        days_ahead=7
    )
    
    if len(all_matches_df) > 0:
        print(f"\n✅ Found {len(all_matches_df)} total matches")
        
        # Group by sport
        for sport in all_matches_df['sport'].unique():
            sport_data = all_matches_df[all_matches_df['sport'] == sport]
            print(f"   - {sport.capitalize()}: {len(sport_data)} matches")
    else:
        print("⚠️  No matches found")


def example_8_continuous_monitoring():
    """Example 8: Set up continuous monitoring for value bets."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Continuous Monitoring Setup")
    print("="*60)
    
    print("\n📊 To set up continuous monitoring in production:")
    print("""
    1. Create a scheduled task (cron, Airflow, etc.) that runs:
       - engine.predict_multiple_matches()
       - every 30 minutes to 1 hour
    
    2. Store recommendations in a database with:
       - match details
       - prediction timestamp
       - odds and edge at prediction time
       - actual result (when match finishes)
    
    3. Calculate tracking metrics:
       - % of recommendations that hit positive edge
       - ROI of following recommendations
       - Model accuracy over time
    
    4. Alert users when:
       - STRONG_BUY opportunity found (edge > 15%)
       - Odds move favorably after prediction
       - Better odds found at alternative bookmakers
    """)


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("🎯 LIVE SPORTS DATA INTEGRATION - EXAMPLES")
    print("="*60)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run examples
        example_1_fetch_live_matches()
        example_2_combine_data_sources()
        example_3_extract_match_features()
        example_4_generate_predictions()
        example_5_find_value_bets()
        example_6_generate_report()
        example_7_multi_sport_analysis()
        example_8_continuous_monitoring()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
