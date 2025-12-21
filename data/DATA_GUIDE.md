# 📊 Historical Match Data Guide

## CSV File Overview

The `data/historical_matches.csv` file contains realistic historical soccer match data for training your AI betting model.

### File Location
```
sports-ai-bettor/
└── data/
    └── historical_matches.csv
```

---

## 📋 Column Description

### Required Columns

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `date` | String | YYYY-MM-DD | Match date |
| `home_team` | String | Any | Home team name |
| `away_team` | String | Any | Away team name |
| `home_form` | Float | 0.0-1.0 | Home team recent form (0=poor, 1=excellent) |
| `away_form` | Float | 0.0-1.0 | Away team recent form (0=poor, 1=excellent) |
| `home_advantage` | Float | 0.0-1.0 | Home advantage factor (typically 0.45-0.60) |
| `recent_goals` | Int | 0-5+ | Recent goals scored by home team |
| `home_shots_on_target` | Int | 0-15+ | Home team shots on target |
| `away_shots_on_target` | Int | 0-15+ | Away team shots on target |
| `home_possession` | Float | 0-100 | Home team possession percentage |
| `away_possession` | Float | 0-100 | Away team possession percentage |
| `home_win` | Int | 0 or 1 | **Target variable** (1=home win, 0=other) |

---

## 📊 Sample Data

### Example Row
```csv
2024-09-01,Arsenal,Liverpool,0.75,0.72,0.55,2,8,6,55,45,1
```

**Interpretation:**
- **Date**: September 1, 2024
- **Teams**: Arsenal (home) vs Liverpool (away)
- **Arsenal form**: 0.75 (strong)
- **Liverpool form**: 0.72 (strong)
- **Home advantage**: 0.55 (moderate)
- **Arsenal recent goals**: 2
- **Arsenal shots on target**: 8
- **Liverpool shots on target**: 6
- **Arsenal possession**: 55%
- **Liverpool possession**: 45%
- **Result**: Arsenal won (1)

---

## 🔢 Data Statistics from Sample File

- **Total matches**: 100
- **Date range**: Sep 1 - Oct 26, 2024
- **Home wins**: ~65%
- **Away wins/Draws**: ~35%

### Feature Ranges

```
home_form:              0.50 - 0.85
away_form:              0.50 - 0.85
home_advantage:         0.45 - 0.60
recent_goals:           0 - 3
home_shots_on_target:   2 - 12
away_shots_on_target:   2 - 11
home_possession:        35 - 68%
away_possession:        32 - 65%
```

---

## 🎯 How to Use This Data

### 1. Train the Model

```bash
python cli_app.py train --data-file data/historical_matches.csv --target home_win
```

Or using the example script:

```bash
python train_example.py
```

### 2. Using in Python Code

```python
import pandas as pd
from src.predictor import get_model_manager

# Load data
df = pd.read_csv('data/historical_matches.csv')

# Train model
manager = get_model_manager()
metrics = manager.train(df, target_col='home_win')

print(f"Accuracy: {metrics['accuracy']:.4f}")
```

### 3. Making Predictions

```python
# Make prediction with the same features as training
features = [0.80, 0.45, 0.55, 2.5, 9, 4, 62, 38]
prediction = manager.predict(features)
print(prediction)
```

---

## 📈 Creating Your Own Data

### Data Source Options

1. **API Sports** (Recommended)
   - https://www.api-football.com/
   - Free tier available
   - Real historical data

2. **Manual Entry**
   - Export from betting sites
   - Spreadsheet data entry

3. **Web Scraping**
   - Stats websites
   - ESPN, StatsBomb, etc.

### Required Features

Your data **must include**:

```
✅ Date (YYYY-MM-DD format)
✅ Home and away team names
✅ Match outcome (home_win: 0 or 1)
✅ At least 3-5 numerical features:
   - Team form/ratings
   - Goal-related stats
   - Possession %
   - Shots on target
   - Any other relevant metric
```

### Data Quality Checklist

```
✅ No missing values (fill with average or remove rows)
✅ Correct data types (numeric columns should be numbers)
✅ Consistent team names (no typos, spacing issues)
✅ Valid date format
✅ Feature values in reasonable ranges (0-1 or 0-100)
✅ At least 50+ matches for training
✅ Balanced target variable (more data the better)
```

---

## 📝 Feature Engineering Tips

### Form Ratings (0-1 scale)

Calculate from recent results:
```
Form = (Recent Wins × 2 + Recent Draws × 1) / (5 matches × 2)

Example: 2 wins, 1 draw in last 5 = (2×2 + 1×1) / 10 = 0.60
```

### Home Advantage Factor

Typical values:
```
0.45-0.50: No clear advantage
0.50-0.55: Slight advantage (small stadium)
0.55-0.60: Strong advantage (large stadium, good fans)
0.60+:     Dominant (championship teams)
```

### Possession & Shots

Better metrics:
```
Shots on Target: More important than total shots
Possession %:    48-52% means balanced, extremes may indicate style
Expected Goals:  xG (if available) is better than shots
```

---

## 🔄 Expanding Your Dataset

### Strategy for Better Model

1. **Start small** (50-100 matches)
   - Train and validate
   - Check accuracy

2. **Add more leagues**
   - Premier League
   - La Liga
   - Bundesliga
   - Serie A

3. **Include more seasons**
   - 2023-2024
   - 2022-2023
   - 2021-2022

4. **Add advanced features**
   - Expected Goals (xG)
   - Team strength ratings
   - Injury reports
   - Head-to-head records

---

## 📊 Data Format Examples

### Simple Format (Minimum)
```csv
date,home_team,away_team,home_form,away_form,home_win
2024-09-01,Arsenal,Liverpool,0.75,0.72,1
2024-09-02,Chelsea,Man United,0.70,0.68,0
```

### Standard Format (Recommended)
```csv
date,home_team,away_team,home_form,away_form,home_advantage,recent_goals,home_shots,away_shots,home_possession,home_win
2024-09-01,Arsenal,Liverpool,0.75,0.72,0.55,2,8,6,55,1
```

### Extended Format (Advanced)
```csv
date,home_team,away_team,home_rank,away_rank,home_form,away_form,home_advantage,recent_goals,home_shots,away_shots,home_possession,home_injuries,away_injuries,head_to_head_home,xg_home,xg_away,home_win
2024-09-01,Arsenal,Liverpool,3,1,0.75,0.72,0.55,2,8,6,55,1,0,0.4,1.8,1.5,1
```

---

## ⚠️ Common Issues & Solutions

### Issue: Accuracy too low (<55%)

**Solutions:**
- More data (add 100+ more matches)
- Better features (use xG, not just shots)
- Data validation (check for errors/outliers)
- Feature scaling (normalize 0-1 range)

### Issue: Model overfitting

**Solutions:**
- Add more diverse data
- Increase test_size (default 0.2)
- Add regularization
- Simplify features

### Issue: Import errors

**Solution:**
```bash
# Make sure you're in project root
cd /Users/apple/sports-ai-bettor

# Install dependencies
pip install -r requirements.txt

# Then run
python train_example.py
```

---

## 🎯 Next Steps

1. **✅ CSV Ready**: Use provided `data/historical_matches.csv`

2. **Train Model**:
   ```bash
   python train_example.py
   ```

3. **Make Predictions**:
   ```bash
   # CLI
   python cli_app.py predict --features 0.7 0.6 0.5 2 9 4 62 38
   
   # Web Dashboard
   streamlit run web_app.py
   ```

4. **Improve Model**:
   - Collect more data
   - Add better features
   - Validate predictions against real results

---

## 📚 Resources

- [API Sports Documentation](https://www.api-football.com/documentation)
- [Pandas CSV Guide](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [Feature Engineering Guide](https://en.wikipedia.org/wiki/Feature_engineering)

---

**You're ready to train your AI bettor! 🚀**

For detailed model training, see [train_example.py](../train_example.py)
