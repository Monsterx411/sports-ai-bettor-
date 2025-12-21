# Sports AI Bettor - Quick Reference

## 🚀 5-Minute Startup

```bash
# 1. Set API keys (optional)
nano .env
# Add: API_SPORTS_KEY=your_key
# Add: ODDS_API_KEY=your_key

# 2. Train model
python train_example.py

# 3. Choose one:
python cli_app.py predict --model-name soccer_model_v1 --features 0.7 --features 0.6 --features 0.5 --features 2 --features 8 --features 5 --features 62 --features 38
# OR
streamlit run web_app.py
```

---

## 📋 All Commands

| Task | Command |
|------|---------|
| **Train Model** | `python train_example.py` |
| **CLI Predict** | `python cli_app.py predict --help` |
| **Web Dashboard** | `streamlit run web_app.py` |
| **Fetch Data** | `python src/data_fetch.py` |
| **Run Tests** | `pytest tests/ -v` |
| **Check Style** | `flake8 src/` |
| **Format Code** | `black src/` |
| **Check Types** | `mypy src/` |

---

## 🔧 Configuration

**File**: `.env`

```env
# API Keys (optional)
API_SPORTS_KEY=YOUR_KEY_HERE
ODDS_API_KEY=YOUR_KEY_HERE

# Settings
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
DEFAULT_SPORT=soccer
EDGE_THRESHOLD=0.05
MIN_CONFIDENCE=0.6
```

---

## 📊 Data Sources

| Source | Setup | Status |
|--------|-------|--------|
| **CSV** | None needed | ✅ Ready |
| **API Football** | Get key + add to .env | Optional |
| **Odds API** | Get key + add to .env | Optional |

---

## 📁 Files You'll Use Most

| File | Purpose |
|------|---------|
| `.env` | Your configuration |
| `train_example.py` | Train the model |
| `cli_app.py` | Make predictions |
| `web_app.py` | Web dashboard |
| `data/historical_matches.csv` | Training data |
| `models/soccer_model_v1.pkl` | Trained model |

---

## 🔑 Get API Keys (Free)

1. **API Football**
   - Visit: https://www.api-football.com/
   - Signup → Dashboard → Copy API key
   - Add to `.env`: `API_SPORTS_KEY=your_key`

2. **The Odds API**
   - Visit: https://theoddsapi.com/
   - Signup → Copy API key
   - Add to `.env`: `ODDS_API_KEY=your_key`

---

## 💡 Example Workflows

### Workflow 1: Quick Test
```bash
python train_example.py
# ✅ Model trained
```

### Workflow 2: Make One Prediction
```bash
python cli_app.py predict \
  --model-name soccer_model_v1 \
  --features 0.7 --features 0.6 --features 0.5 \
  --features 2 --features 8 --features 5 \
  --features 62 --features 38
```

### Workflow 3: Interactive Dashboard
```bash
streamlit run web_app.py
# Opens browser: http://localhost:8501
```

### Workflow 4: Fetch Live Data
```bash
# First add API_SPORTS_KEY to .env
python src/data_fetch.py
```

---

## ⚡ Predict Feature Order

When making predictions, use features in this order:

1. `home_form` (0-1)
2. `away_form` (0-1)
3. `home_advantage` (0-1)
4. `recent_goals` (0-5)
5. `home_shots_on_target` (0-15)
6. `away_shots_on_target` (0-15)
7. `home_possession` (30-70)
8. `away_possession` (30-70)

Example:
```
0.7 (home_form) 0.6 (away_form) 0.5 (home_advantage) 
2 (recent_goals) 8 (home_shots) 5 (away_shots) 
62 (home_possession) 38 (away_possession)
```

---

## 🧪 Quick Tests

```bash
# Check config loads
python -c "from config.settings import settings; print('✅ Config OK')"

# Check data loads
python -c "import pandas; print(f'✅ Loaded {len(pandas.read_csv(\"data/historical_matches.csv\"))} matches')"

# Check imports
python -c "import sklearn, streamlit, click; print('✅ All imports OK')"
```

---

## 📞 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `pip install -r requirements.txt --break-system-packages` |
| .env not found | `cp .env.example .env` |
| API connection failed | Check API key in `.env` |
| Low accuracy | Add more training data |
| Port already in use (Streamlit) | `streamlit run web_app.py --server.port=8502` |

---

## 📚 Learn More

- Full setup: `SETUP_GUIDE.md`
- API reference: `docs/API_REFERENCE.md`
- Data format: `data/DATA_GUIDE.md`
- Advanced: `docs/ADVANCED_USAGE.md`

---

**Your environment is ready to go! 🎯**
