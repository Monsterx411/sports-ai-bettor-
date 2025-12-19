"""
API Reference - Sports AI Bettor

## Core Modules

### src.data_fetch

Fetch sports data from APIs with caching and retry logic.

#### SportsDataFetcher

Main class for fetching sports data.

**Methods:**

- `fetch_fixtures(sport='soccer', league='premier_league', season=2025) -> pd.DataFrame`
  - Fetch upcoming fixtures
  
- `fetch_odds(event_id: str, region='us') -> Dict[str, float]`
  - Fetch betting odds for an event
  
- `fetch_team_stats(team_id: int, season=2025) -> Dict[str, Any]`
  - Fetch team statistics
  
- `clear_cache() -> None`
  - Clear cached data

**Example:**

```python
from src.data_fetch import get_fetcher

fetcher = get_fetcher()
fixtures = fetcher.fetch_fixtures(league='premier_league')
odds = fetcher.fetch_odds('event_123')
```

### src.predictor

ML model training and predictions.

#### ModelManager

Manage machine learning models.

**Methods:**

- `train(df, target_col='home_win', feature_cols=None, model_name='sports_model') -> Dict`
  - Train RandomForest classifier
  
- `predict(features: List[float]) -> Dict[str, float]`
  - Make prediction for single sample
  
- `predict_batch(features_df: pd.DataFrame) -> np.ndarray`
  - Make predictions for multiple samples
  
- `get_feature_importance() -> Dict[str, float]`
  - Get feature importance scores
  
- `save(model_name: str) -> bool`
  - Save model to disk
  
- `load(model_name: str) -> bool`
  - Load model from disk

**Example:**

```python
from src.predictor import get_model_manager
import pandas as pd

manager = get_model_manager()
df = pd.read_csv('data/historical.csv')
metrics = manager.train(df)
prediction = manager.predict([0.7, 0.6, 0.5])
```

#### BetAnalyzer

Analyze predictions and find value bets.

**Static Methods:**

- `calculate_implied_probability(odds: float) -> float`
  - Calculate implied probability from odds
  
- `calculate_expected_value(probability: float, odds: float, stake: float = 1.0) -> float`
  - Calculate bet expected value
  
- `find_value_bets(predictions: Dict, odds: Dict, min_edge: float = None) -> List[Dict]`
  - Find value betting opportunities
  
- `calculate_kelly_criterion(probability: float, odds: float) -> float`
  - Calculate optimal bet size using Kelly Criterion

**Example:**

```python
from src.predictor import BetAnalyzer

predictions = {'class_1_prob': 0.65}
odds = {'Home': 1.80}

bets = BetAnalyzer.find_value_bets(predictions, odds, min_edge=0.05)
kelly = BetAnalyzer.calculate_kelly_criterion(0.65, 1.80)
```

### src.logger

Logging configuration.

**Functions:**

- `setup_logger(name: str, level: str = None, log_file: bool = True) -> logging.Logger`
  - Create configured logger instance

**Example:**

```python
from src.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Application started")
logger.error("An error occurred")
```

### src.utils

Utility functions.

**Functions:**

- `safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any`
  - Safely access nested dictionary values
  
- `format_currency(value: float, symbol: str = '$') -> str`
  - Format value as currency
  
- `format_percentage(value: float, decimals: int = 2) -> str`
  - Format value as percentage
  
- `export_json(data: Dict, filename: str) -> bool`
  - Export data to JSON file
  
- `import_json(filename: str) -> Dict`
  - Import data from JSON file
  
- `get_timestamp() -> str`
  - Get current timestamp in ISO format

**Example:**

```python
from src.utils import safe_get, format_percentage, export_json

data = {'user': {'odds': {'home': 1.80}}}
value = safe_get(data, ['user', 'odds', 'home'])

percentage = format_percentage(0.65)
export_json({'data': value}, 'output.json')
```

## Configuration

### config.settings

Application settings management.

**Class: Settings**

Static configuration values loaded from environment variables.

**Key Attributes:**

- `API_SPORTS_KEY`: Sports API key
- `ODDS_API_KEY`: Odds API key
- `ENVIRONMENT`: App environment (development/production)
- `DEBUG`: Debug mode flag
- `LOG_LEVEL`: Logging level
- `EDGE_THRESHOLD`: Minimum edge for value bets
- `MIN_CONFIDENCE`: Minimum confidence threshold
- `CACHE_ENABLED`: Enable response caching
- `CACHE_TTL`: Cache time-to-live in seconds

**Example:**

```python
from config.settings import settings

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Cache enabled: {settings.CACHE_ENABLED}")
```

## CLI Commands

```bash
# Fetch fixtures
python cli_app.py fixtures --sport soccer --league premier_league

# Train model
python cli_app.py train --data-file data/historical.csv --target home_win

# Make predictions
python cli_app.py predict --model-name sports_model --features 0.7 0.6 0.5

# Analyze match
python cli_app.py analyze --event-id 123 --odds Home 1.80 --odds Away 2.50

# Show settings
python cli_app.py settings

# Show version
python cli_app.py version
```

## Error Handling

All modules include comprehensive error handling:

```python
try:
    manager = get_model_manager()
    prediction = manager.predict(features)
    if not prediction:
        logger.error("Prediction failed")
except Exception as e:
    logger.error(f"Error: {e}")
```

## Logging Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical messages for very serious problems

Set via environment variable:

```bash
export LOG_LEVEL=DEBUG
python cli_app.py fixtures
```

---

For more examples and usage, see README.md and inline code documentation.
"""