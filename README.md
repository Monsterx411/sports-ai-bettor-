# 🎯 Sports AI Bettor

**AI-powered sports betting predictions with intelligent value bet identification.**

An advanced machine learning system that predicts sports match outcomes and identifies profitable betting opportunities using Real-time odds analysis and predictive modeling.

---

## 📋 Features

- **🤖 ML-Powered Predictions**: RandomForest classifier for accurate match outcome predictions
- **💰 Value Bet Detection**: Identifies bets with positive expected value edge
- **📊 Odds Analysis**: Kelly Criterion, implied probability, and EV calculations
- **🔄 Real-Time Data**: API integration with sports data and betting odds providers
- **💾 Intelligent Caching**: Reduces API calls and improves performance
- **📈 Web Dashboard**: Interactive Streamlit interface for analysis
- **🖥️ CLI Tools**: Command-line interface for batch operations
- **📋 Robust Logging**: Comprehensive logging for debugging and monitoring
- **⚙️ Configuration Management**: Environment-based settings and API key management

---

## 🏗️ Project Structure

```
sports-ai-bettor/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── data_fetch.py            # Sports API client with caching & retries
│   ├── predictor.py             # ML model training & predictions
│   ├── logger.py                # Logging configuration
│   └── utils.py                 # Utility functions
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration management
├── tests/
│   ├── test_data_fetch.py       # Data fetcher tests
│   ├── test_predictor.py        # Model tests
│   └── conftest.py              # Pytest configuration
├── models/                      # Trained model storage (gitignored)
├── data/                        # Dataset storage (gitignored)
├── logs/                        # Application logs (gitignored)
├── docs/                        # Documentation
├── cli_app.py                   # CLI entry point
├── web_app.py                   # Streamlit web interface
├── requirements.txt             # Dependencies
├── setup.py                     # Package setup
├── pyproject.toml              # Project metadata & tool config
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Monsterx411/sports-ai-bettor.git
   cd sports-ai-bettor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or for development:
   pip install -e ".[dev]"
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env
   ```

### Usage

#### Web Dashboard
```bash
streamlit run web_app.py
```
Access at `http://localhost:8501`

#### Command Line
```bash
# View help
python cli_app.py --help

# Fetch fixtures
python cli_app.py fixtures --sport soccer --league premier_league

# Train model
python cli_app.py train --data-file data/historical.csv --target home_win

# Make predictions
python cli_app.py predict --model-name sports_model --features 0.7 0.6 0.5

# Analyze match and find value bets
python cli_app.py analyze --event-id match_123 \
  --odds Home 1.80 --odds Away 2.50 \
  --odds Draw 3.50

# Display settings
python cli_app.py settings
```

---

## 🔧 Configuration

Configuration is managed through environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_SPORTS_KEY` | - | API Sports API key |
| `ODDS_API_KEY` | - | The Odds API key |
| `ENVIRONMENT` | development | App environment (development/production) |
| `LOG_LEVEL` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `EDGE_THRESHOLD` | 0.05 | Minimum edge % for value bets |
| `MIN_CONFIDENCE` | 0.6 | Minimum confidence for predictions |
| `CACHE_ENABLED` | true | Enable response caching |
| `CACHE_TTL` | 3600 | Cache time-to-live in seconds |

---

## 📚 API Documentation

### Data Fetcher

```python
from src.data_fetch import get_fetcher

fetcher = get_fetcher()

# Fetch fixtures
fixtures = fetcher.fetch_fixtures(sport="soccer", league="premier_league")

# Fetch odds
odds = fetcher.fetch_odds(event_id="12345")

# Fetch team stats
stats = fetcher.fetch_team_stats(team_id=1)

# Clear cache
fetcher.clear_cache()
```

### Predictor

```python
from src.predictor import get_model_manager, BetAnalyzer

manager = get_model_manager()

# Train model
metrics = manager.train(df, target_col="home_win")

# Make prediction
prediction = manager.predict([0.7, 0.6, 0.5])

# Get feature importance
importances = manager.get_feature_importance()

# Save/Load models
manager.save("my_model")
manager.load("my_model")
```

### Bet Analysis

```python
from src.predictor import BetAnalyzer

# Find value bets
bets = BetAnalyzer.find_value_bets(predictions, odds, min_edge=0.05)

# Calculate implied probability
prob = BetAnalyzer.calculate_implied_probability(odds=1.80)

# Calculate expected value
ev = BetAnalyzer.calculate_expected_value(probability=0.6, odds=1.80)

# Kelly Criterion sizing
kelly = BetAnalyzer.calculate_kelly_criterion(probability=0.6, odds=1.80)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov=config --cov-report=html

# Specific test file
pytest tests/test_predictor.py -v
```

---

## 📦 Model Training Example

```python
import pandas as pd
from src.predictor import get_model_manager

# Load your historical data
df = pd.read_csv('data/historical_matches.csv')

# Should contain columns: home_win, home_form, away_form, home_advantage, etc.

# Train model
manager = get_model_manager()
metrics = manager.train(df, target_col='home_win', model_name='soccer_v1')

print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1 Score: {metrics['f1']:.4f}")
```

---

## 💡 Value Bet Logic

The system identifies value bets using:

1. **Predicted Probability**: ML model output
2. **Implied Probability**: Calculated from odds (1/odds)
3. **Edge Calculation**: Predicted Probability - Implied Probability
4. **Expected Value**: (Probability × Profit) - ((1-Probability) × Stake)

A bet is considered a **value bet** when:
- Edge > EDGE_THRESHOLD (default: 5%)
- Predicted Probability > MIN_CONFIDENCE (default: 60%)

---

## 🔐 Security Notes

- **Never commit `.env` files** with real API keys
- Always use environment variables for sensitive data
- The `.env.example` file shows required variables
- Use `.gitignore` to prevent accidental commits

---

## 🐛 Debugging

Enable debug mode for verbose logging:

```bash
# CLI
python cli_app.py --debug fixtures

# Environment
export DEBUG=true
export LOG_LEVEL=DEBUG
python cli_app.py fixtures
```

Logs are saved to `logs/` directory.

---

## 📈 Performance Optimization

### Caching
- API responses are cached by default
- Cache TTL: 1 hour for fixtures, 30 min for odds
- Clear cache: `fetcher.clear_cache()`

### Parallel Processing
- RandomForest uses all available CPU cores (`n_jobs=-1`)
- Batch predictions available via `predict_batch()`

### API Efficiency
- Automatic retry with exponential backoff
- Connection pooling for HTTP requests
- Timeout handling to prevent hangs

---

## 🤝 Contributing

Contributions welcome! Please:

1. Create a feature branch
2. Follow PEP 8 style guide
3. Add tests for new features
4. Update documentation
5. Submit pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## ⚠️ Disclaimer

**This tool is for research and educational purposes only.**

- Past performance doesn't guarantee future results
- Betting involves significant financial risk
- Always gamble responsibly
- Seek professional financial advice before trading
- The authors assume no liability for losses

---

## 🔗 Resources

- [API Sports Documentation](https://www.api-football.com/)
- [The Odds API](https://the-odds-api.com/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs in `logs/` directory

---

**Built with ❤️ for sports betting enthusiasts**
