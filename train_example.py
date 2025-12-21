#!/usr/bin/env python3
"""
Example script: Training the Sports AI Bettor model with historical data.
Demonstrates how to use the CSV file to train and make predictions.
"""

import pandas as pd
from src.predictor import get_model_manager, BetAnalyzer
from src.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Train model and demonstrate predictions."""
    
    # Step 1: Load historical data
    print("\n📊 Loading historical match data...")
    df = pd.read_csv('data/historical_matches.csv')
    print(f"✅ Loaded {len(df)} matches")
    print(f"   Columns: {', '.join(df.columns.tolist())}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Home wins: {df['home_win'].sum()} out of {len(df)}")
    
    # Step 2: Check data quality
    print("\n🔍 Data quality check...")
    print(f"   Missing values: {df.isnull().sum().sum()}")
    print(f"   Data types:\n{df.dtypes}")
    
    # Step 3: Train model
    print("\n🤖 Training RandomForest model...")
    manager = get_model_manager()
    
    # Drop non-numeric columns (date, team names) before training
    df_numeric = df.drop(columns=['date', 'home_team', 'away_team'])
    
    # The model will automatically use all columns except 'home_win' as features
    metrics = manager.train(
        df_numeric,
        target_col='home_win',
        model_name='soccer_model_v1'
    )
    
    # Step 4: Display results
    print("\n📈 Model Training Results:")
    print(f"   Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"   Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"   Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"   F1 Score:  {metrics['f1']:.4f}")
    
    # Step 5: Get feature importance
    print("\n⭐ Feature Importance:")
    importances = manager.get_feature_importance()
    for feature, importance in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(importance * 50)
        print(f"   {feature:25s} {bar} {importance:.4f}")
    
    # Step 6: Make a sample prediction
    print("\n🔮 Making a sample prediction...")
    # Example: A match with good home form vs weak away form
    sample_features = [
        0.80,  # home_form (strong)
        0.45,  # away_form (weak)
        0.55,  # home_advantage
        2.5,   # recent_goals
        9,     # home_shots_on_target
        4,     # away_shots_on_target
        62,    # home_possession
        38     # away_possession
    ]
    
    prediction = manager.predict(sample_features)
    print("   Sample match stats:")
    print(f"      Home form: 0.80 (strong)")
    print(f"      Away form: 0.45 (weak)")
    print(f"      Home advantage: 0.55")
    print(f"      Recent goals: 2.5")
    print(f"\n   Prediction probabilities:")
    for class_name, prob in prediction.items():
        print(f"      {class_name}: {prob:.2%}")
    
    # Step 7: Value betting example
    print("\n💰 Value Bet Analysis Example:")
    # Hypothetical odds
    odds = {
        '0': 3.50,  # Away win
        '1': 1.80   # Home win
    }
    
    value_bets = BetAnalyzer.find_value_bets(prediction, odds, min_edge=0.03)
    
    if value_bets:
        print("   Value bets found:")
        for bet in value_bets:
            print(f"      Outcome: {bet['outcome']}")
            print(f"      Odds: {bet['odds']}")
            print(f"      Predicted Probability: {bet['predicted_probability']:.2%}")
            print(f"      Implied Probability: {bet['implied_probability']:.2%}")
            print(f"      Edge: {bet['edge']:.2%}")
            print(f"      Expected Value: {bet['expected_value']:.4f}")
            print(f"      Recommendation: {bet['recommendation']}\n")
    else:
        print("   No value bets with current odds")
    
    # Step 8: Kelly Criterion example
    print("\n📊 Kelly Criterion Bet Sizing:")
    bankroll = 1000  # $1000 bankroll
    
    for class_name, prob in prediction.items():
        if class_name == '1':  # Home win
            odds_value = odds.get('1', 0)
            if odds_value > 0:
                kelly = BetAnalyzer.calculate_kelly_criterion(prob, odds_value)
                bet_size = bankroll * kelly
                safe_bet = bet_size * 0.25  # 25% Kelly for safety
                
                print(f"   For home win prediction ({prob:.2%}):")
                print(f"      Full Kelly: ${bet_size:.2f} ({kelly:.1%} of bankroll)")
                print(f"      Safe Kelly (25%): ${safe_bet:.2f}")
    
    print("\n✅ Training complete! Model saved as 'soccer_model_v1'")
    print("\n📝 Next steps:")
    print("   1. Use cli_app.py predict command for new matches")
    print("   2. Use web_app.py for interactive predictions")
    print("   3. Collect more data to improve model accuracy")


if __name__ == '__main__':
    main()
