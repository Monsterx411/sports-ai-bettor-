# Sports AI Bettor - Complete Setup Guide

## 📋 Setup Overview

This guide walks you through setting up the complete Sports AI Bettor environment for:
- ✅ Model training with CSV data (no API needed)
- ✅ Live data fetching from sports APIs
- ✅ CLI predictions
- ✅ Interactive web dashboard

---

## ✅ Current Environment Status

### System Information
```
Python Version:  3.14.2 (System Python)
Environment:     macOS
Project Root:    /Users/apple/sports-ai-bettor
```

### Installed Packages ✅
- **Data**: pandas, numpy, scipy
- **ML**: scikit-learn
- **Web**: streamlit, click, plotly
- **Visualization**: matplotlib, seaborn
- **Development**: pytest, black, flake8, mypy
- **Other**: requests, python-dotenv, pytz

---

## 🚀 Quick Start (3 commands)

### 1. Set Environment Variables
```bash
# Edit .env file with your API keys
nano .env
```

Add your API keys:
```env
API_SPORTS_KEY=your_api_sports_key_here
ODDS_API_KEY=your_odds_api_key_here
```

### 2. Train the Model
```bash
python train_example.py
```

Output:
```
✅ Accuracy:  94.44%
✅ Precision: 95.00%
✅ Model saved: models/soccer_model_v1.pkl
```

### 3. Start Using It
```bash
# Option A: Web Dashboard
streamlit run web_app.py

# Option B: CLI Predictions
python cli_app.py predict --model-name soccer_model_v1 \
  --features 0.7 --features 0.6 --features 0.5 \
  --features 2 --features 8 --features 5 \
  --features 62 --features 38
```

---

## 🔧 Environment Configuration

### Configuration Files

**Location**: `.env` (in project root)

**Current Status**: ✅ Created and ready

### Available Settings

```env
# ========================================
# API KEYS (Optional - for live data)
# ========================================
API_SPORTS_KEY=YOUR_KEY              # From https://api-football.com/
ODDS_API_KEY=YOUR_KEY                # From https://theoddsapi.com/

# ========================================
# APPLICATION
# ========================================
ENVIRONMENT=development              # development, staging, production
DEBUG=false                           # Enable debug logging
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# ========================================
# BETTING PARAMETERS
# ========================================
DEFAULT_SPORT=soccer                 # Sport to analyze
EDGE_THRESHOLD=0.05                  # Minimum edge (5%)
MIN_CONFIDENCE=0.6                   # Minimum prediction confidence

# ========================================
# ML MODEL
# ========================================
RANDOM_FOREST_ESTIMATORS=100         # Number of trees
TEST_SIZE=0.2                        # Test/train split (20%)
RANDOM_STATE=42                      # Reproducibility

# ========================================
# API REQUESTS
# ========================================
REQUEST_TIMEOUT=10                   # Timeout in seconds
MAX_RETRIES=3                        # Retry attempts
RETRY_BACKOFF=1.5                    # Backoff multiplier

# ========================================
# CACHING
# ========================================
CACHE_ENABLED=true                   # Enable caching
CACHE_TTL=3600                       # Cache time-to-live (1 hour)
```

---

## 📊 Data Sources Available

### Option 1: CSV Data (✅ Ready to Use)

**No API setup needed!**

```bash
# File: data/historical_matches.csv
# Size: 100 match records
# Date Range: Sept 1 - Oct 26, 2024
# Ready to use immediately

python train_example.py
```

**Features Available:**
- home_team, away_team
- home_form, away_form (0-1 range)
- home_advantage
- shots_on_target, possession
- And more...

---

### Option 2: API Sports (Live Data)

**For live fixture and match data**

1. **Get API Key**
   - Visit: https://www.api-football.com/
   - Create free account
   - Copy your API key

2. **Add to Environment**
   ```bash
   nano .env
   # Add: API_SPORTS_KEY=your_key_here
   ```

3. **Test Connection**
   ```bash
   python src/data_fetch.py
   ```

**What You Can Fetch:**
- Fixture data
- Match statistics
- Team information
- Standings
- Predictions

**Code Example:**
```python
from src.data_fetch import SportsDataFetcher

fetcher = SportsDataFetcher()
fixtures = fetcher.get_fixtures(league="39", season="2024")
```

---

### Option 3: The Odds API (Betting Odds)

**For real-time betting odds**

1. **Get API Key**
   - Visit: https://theoddsapi.com/
   - Create free account
   - Copy your API key

2. **Add to Environment**
   ```bash
   nano .env
   # Add: ODDS_API_KEY=your_key_here
   ```

3. **Test Connection**
   ```python
   from src.data_fetch import SportsDataFetcher
   
   fetcher = SportsDataFetcher()
   odds = fetcher.get_odds(sport="soccer")
   ```

---

## 🎯 Complete Workflow

### Step 1: Model Training

```bash
# Using CSV (recommended for first-time)
python train_example.py

# Output:
# ✅ Loaded 88 matches
# ✅ Accuracy: 94.44%
# ✅ Model saved to models/soccer_model_v1.pkl
```

### Step 2: Make Predictions

**Option A: CLI**
```bash
python cli_app.py predict \
  --model-name soccer_model_v1 \
  --features 0.7 --features 0.6 --features 0.5 \
  --features 2 --features 8 --features 5 \
  --features 62 --features 38

# Output:
# class_0_prob: 27.00%
# class_1_prob: 73.00%  ← Home team wins
```

**Option B: Web Dashboard**
```bash
streamlit run web_app.py
# Opens: http://localhost:8501
```

**Option C: Python Code**
```python
from src.predictor import get_model_manager

manager = get_model_manager()
manager.load_model('soccer_model_v1')

features = [0.7, 0.6, 0.5, 2, 8, 5, 62, 38]
prediction = manager.predict(features)
```

### Step 3: Analyze Value Bets

```python
from src.predictor import BetAnalyzer

analyzer = BetAnalyzer()
odds = 1.8  # Real odds from bookmaker
predicted_prob = 0.73  # From model

value_bet = analyzer.find_value_bets(
    prediction_probs={'home_win': predicted_prob},
    odds={'home_win': odds}
)

print(f"Edge: {value_bet['edge']*100:.2f}%")
print(f"Expected Value: {value_bet['expected_value']}")
print(f"Kelly Criterion: {value_bet['kelly_criterion']}")
```

---

## 🔌 Project Architecture

### Directory Structure
```
sports-ai-bettor/
├── .env                    ← Your configuration
├── .env.example            ← Template
├── requirements.txt        ← Python dependencies
├── setup.sh / setup_project.py  ← Setup scripts
│
├── src/                    ← Core modules
│   ├── data_fetch.py       ← API clients & data fetching
│   ├── predictor.py        ← ML model & predictions
│   ├── logger.py           ← Logging system
│   └── utils.py            ← Helper functions
│
├── config/                 ← Configuration
│   ├── settings.py         ← Central settings (reads .env)
│
├── data/                   ← Data files
│   ├── historical_matches.csv    ← Training data
│   └── DATA_GUIDE.md             ← Data documentation
│
├── models/                 ← Saved ML models
│   └── soccer_model_v1.pkl       ← Trained model
│
├── cli_app.py              ← CLI interface
├── web_app.py              ← Web dashboard (Streamlit)
├── train_example.py        ← Training example
│
├── tests/                  ← Test suite
└── docs/                   ← Documentation
```

### How Configuration Works

1. **Read from .env**
   ```python
   # In .env file:
   API_SPORTS_KEY=abc123
   DEBUG=true
   ```

2. **Access in Code**
   ```python
   from config.settings import settings
   
   print(settings.API_SPORTS_KEY)  # "abc123"
   print(settings.DEBUG)            # True
   ```

3. **Environment Fallbacks**
   - Uses `.env` file values
   - Falls back to defaults if not set
   - Can override with OS environment variables

---

## 🧪 Testing Your Setup

### Test 1: Configuration ✅
```bash
python -c "from config.settings import settings; print(settings.ENVIRONMENT)"
# Output: development
```

### Test 2: Data Loading ✅
```bash
python -c "import pandas as pd; df = pd.read_csv('data/historical_matches.csv'); print(f'Loaded {len(df)} matches')"
# Output: Loaded 88 matches
```

### Test 3: Model Training ✅
```bash
python train_example.py
# Output: Training complete! Model saved as 'soccer_model_v1'
```

### Test 4: CLI Prediction ✅
```bash
python cli_app.py predict --model-name soccer_model_v1 \
  --features 0.7 --features 0.6 --features 0.5 \
  --features 2 --features 8 --features 5 \
  --features 62 --features 38
# Output: class_0_prob: 27.00%, class_1_prob: 73.00%
```

### Test 5: Web Dashboard ✅
```bash
streamlit run web_app.py
# Opens browser to http://localhost:8501
```

---

## 📚 Commands Reference

### Model Operations
```bash
# Train model (with CSV data)
python train_example.py

# Make predictions (CLI)
python cli_app.py predict --help

# Use web interface
streamlit run web_app.py
```

### Data Operations
```bash
# Fetch live data (requires API keys)
python src/data_fetch.py

# Check configuration
python -c "from config.settings import settings; print(settings.to_dict())"
```

### Development
```bash
# Run tests
pytest tests/ -v

# Check code style
flake8 src/ config/

# Format code
black src/ config/ cli_app.py web_app.py

# Type checking
mypy src/ config/
```

---

## 🔑 API Keys Setup

### Step-by-Step: Get Free API Keys

#### API Football
1. Go to: https://www.api-football.com/
2. Click "Get Started Free"
3. Create account
4. Go to "Dashboard" → "API-KEY"
5. Copy your key
6. Add to `.env`:
   ```env
   API_SPORTS_KEY=YOUR_KEY_HERE
   ```

#### The Odds API
1. Go to: https://theoddsapi.com/
2. Sign up free
3. Copy your API key
4. Add to `.env`:
   ```env
   ODDS_API_KEY=YOUR_KEY_HERE
   ```

#### Verify Setup
```bash
# Check that keys are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('API_SPORTS_KEY')[:15])"
```

---

## 🐛 Troubleshooting

### Issue: Module not found
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution:**
```bash
python -m pip install -r requirements.txt --break-system-packages
```

### Issue: .env file not found
```
ValueError: .env file not found
```
**Solution:**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Issue: API connection failed
```
ConnectionError: Unable to connect to API
```
**Solution:**
1. Check your API key in `.env`
2. Verify internet connection
3. Check API status: api-football.com, theoddsapi.com
4. Try: `python src/data_fetch.py` for diagnostics

### Issue: Low prediction accuracy
**Solution:**
1. Add more training data
2. Engineer better features
3. Check data quality
4. Try different models

---

## 📈 Next Steps

1. **Immediate** (No setup needed)
   ```bash
   python train_example.py
   streamlit run web_app.py
   ```

2. **Short-term** (Optional API keys)
   - Get API keys from API Football and Odds API
   - Add to `.env`
   - Test with live data

3. **Long-term** (Advanced)
   - Collect more training data
   - Engineer custom features
   - Deploy to production
   - Integrate with betting exchanges

---

## 📞 Support Resources

### Documentation
- [README.md](README.md) - Project overview
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - Code API
- [data/DATA_GUIDE.md](data/DATA_GUIDE.md) - Data format
- [docs/ADVANCED_USAGE.md](docs/ADVANCED_USAGE.md) - Advanced patterns

### External Resources
- [API Football Docs](https://www.api-football.com/documentation)
- [The Odds API Docs](https://theoddsapi.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [scikit-learn Docs](https://scikit-learn.org/)

---

## ✨ You're All Set!

Your Sports AI Bettor environment is fully configured and ready to:
- ✅ Train models with CSV data
- ✅ Make predictions via CLI or web
- ✅ Fetch live data when you add API keys
- ✅ Analyze value betting opportunities
- ✅ Calculate optimal bet sizing with Kelly Criterion

**Happy betting! 🚀**
