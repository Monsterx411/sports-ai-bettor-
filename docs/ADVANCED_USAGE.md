"""
Advanced Usage Guide - Sports AI Bettor

## Training Your Own Model

### Step 1: Prepare Training Data

Create a CSV file with historical match data:

```csv
home_team,away_team,date,home_form,away_form,home_advantage,recent_goals,home_win
Arsenal,Liverpool,2024-01-15,0.75,0.70,0.55,2,1
Manchester United,Chelsea,2024-01-16,0.60,0.65,0.50,1,0
...
```

Required columns:
- `home_win` (target): 1 for home win, 0 otherwise
- Feature columns: At least 3-5 features for model accuracy

### Step 2: Train Model

```python
import pandas as pd
from src.predictor import get_model_manager

# Load data
df = pd.read_csv('data/historical_matches.csv')

# Train model
manager = get_model_manager()
metrics = manager.train(
    df,
    target_col='home_win',
    model_name='my_soccer_model_v1'
)

print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1 Score: {metrics['f1']:.4f}")
```

### Step 3: Evaluate Model

```python
# Get feature importance
importances = manager.get_feature_importance()
print("Feature Importance:")
for feature, importance in importances.items():
    print(f"  {feature}: {importance:.4f}")
```

## Advanced Prediction

### Using Custom Features

```python
from src.predictor import get_model_manager

manager = get_model_manager()
manager.load('my_soccer_model_v1')

# Extract features from live data
features = [
    home_recent_form,      # 0.75
    away_recent_form,      # 0.60
    home_advantage_score,  # 0.55
    recent_goals_avg,      # 2.1
    injury_impact_score    # 0.8
]

# Make prediction
prediction = manager.predict(features)
print(f"Home Win Probability: {prediction['class_1_prob']:.2%}")
```

### Batch Predictions

```python
import pandas as pd
from src.predictor import get_model_manager

manager = get_model_manager()
manager.load('my_soccer_model_v1')

# Prepare batch data
batch_df = pd.read_csv('upcoming_matches.csv')
features_df = batch_df[['home_form', 'away_form', 'home_advantage', 'recent_goals', 'injuries']]

# Get all predictions
predictions = manager.predict_batch(features_df)
batch_df['prediction'] = predictions
batch_df.to_csv('predictions.csv', index=False)
```

## Value Betting Strategy

### Finding Value Across Books

```python
from src.predictor import BetAnalyzer

# Your model prediction
prediction = {'class_1_prob': 0.65}  # 65% home win probability

# Odds from different sportsbooks
bookmakers = {
    'DraftKings': {'Home': 1.70, 'Away': 2.20, 'Draw': 3.50},
    'FanDuel': {'Home': 1.75, 'Away': 2.15, 'Draw': 3.40},
    'BetMGM': {'Home': 1.80, 'Away': 2.10, 'Draw': 3.45}
}

# Find best value
best_bets = {}
for book, odds in bookmakers.items():
    bets = BetAnalyzer.find_value_bets(prediction, odds, min_edge=0.03)
    if bets:
        best_bets[book] = bets[0]
        print(f"{book}: {bets[0]['recommendation']}")
```

### Kelly Criterion Bet Sizing

```python
from src.predictor import BetAnalyzer

# Your bankroll
bankroll = 10000

# For each value bet
prediction_prob = 0.65
odds = 1.80

# Calculate Kelly optimal bet
kelly_fraction = BetAnalyzer.calculate_kelly_criterion(prediction_prob, odds)
bet_size = bankroll * kelly_fraction

print(f"Optimal bet: ${bet_size:.2f} ({kelly_fraction:.1%} of bankroll)")

# For safety, use fractional Kelly (e.g., 25% Kelly)
safe_bet_size = bet_size * 0.25
print(f"Conservative bet: ${safe_bet_size:.2f}")
```

## API Integration

### Custom Data Provider

```python
from src.data_fetch import APIClient
from config.settings import settings
from src.logger import setup_logger

logger = setup_logger(__name__)

class CustomSportsAPI(APIClient):
    """Custom integration with your data source."""
    
    def fetch_custom_data(self, match_id):
        url = f"https://your-api.com/matches/{match_id}"
        headers = {"Authorization": f"Bearer {settings.CUSTOM_API_KEY}"}
        
        data = self.get(url, headers=headers)
        if data:
            logger.info(f"Custom data fetched for {match_id}")
            return data
        return None
```

## Monitoring & Logging

### Custom Logger Configuration

```python
import logging
from src.logger import setup_logger

# Create loggers for different components
data_logger = setup_logger('data_fetch', level='DEBUG')
model_logger = setup_logger('predictor', level='INFO')
api_logger = setup_logger('api_client', level='WARNING')

# Use in your code
data_logger.debug("Fetching fixtures...")
model_logger.info("Model training complete")
api_logger.warning("API rate limit warning")
```

### Performance Monitoring

```python
import time
from src.logger import setup_logger

logger = setup_logger(__name__)

def monitor_predictions(predictions_list, labels):
    """Monitor prediction performance over time."""
    
    correct = sum(1 for pred, label in zip(predictions_list, labels) if pred == label)
    accuracy = correct / len(labels)
    
    logger.info(f"Prediction Accuracy: {accuracy:.4f}")
    logger.info(f"Predictions tested: {len(labels)}")

# Log to monitor file
monitor_predictions(predictions, actual_outcomes)
```

## Production Deployment

### Environment Configuration

Create `.env.production`:

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

API_SPORTS_KEY=your_production_key
ODDS_API_KEY=your_production_key

CACHE_TTL=7200
REQUEST_TIMEOUT=5
MAX_RETRIES=5
```

### Running Web App

```bash
# Development
streamlit run web_app.py

# Production (Streamlit Cloud, Docker, etc.)
streamlit run web_app.py \
  --logger.level=error \
  --client.showErrorDetails=false
```

### CLI Automation

```bash
#!/bin/bash
# daily_predictions.sh

export ENVIRONMENT=production
export LOG_LEVEL=INFO

cd /path/to/sports-ai-bettor

# Fetch today's fixtures
python cli_app.py fixtures --sport soccer --output fixtures.csv

# Make predictions
python cli_app.py predict --model-name production_model \
  --features 0.7 0.6 0.5 > predictions.json

# Archive results
mkdir -p results/$(date +%Y-%m-%d)
mv predictions.json results/$(date +%Y-%m-%d)/
```

## Performance Optimization

### Caching Strategy

```python
from src.data_fetch import get_fetcher
from config.settings import settings

fetcher = get_fetcher()

# Fixtures have long cache (1 hour)
fixtures = fetcher.fetch_fixtures()

# Odds have short cache (30 min) - set via API
odds = fetcher.fetch_odds('event_123')

# Clear cache when needed
fetcher.clear_cache()
```

### Parallel Processing

```python
from src.predictor import get_model_manager
import pandas as pd
from multiprocessing import Pool

manager = get_model_manager()
manager.load('my_model')

# Batch predict leverages multiple CPU cores
matches_df = pd.read_csv('upcoming_matches.csv')
features = matches_df[['form', 'goals', 'advantage']]
predictions = manager.predict_batch(features)  # Uses all cores automatically
```

---

For more help, see the API Reference (docs/API_REFERENCE.md) and README.md
"""