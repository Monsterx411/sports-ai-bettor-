# 🎯 CSV DATABASE SETUP & MODEL TRAINING GUIDE

## 📊 Your Data File

**Location**: `data/historical_matches.csv`  
**Format**: 100 historical soccer match records  
**Ready to use**: ✅ YES

---

## 🚀 QUICK START - 3 Ways to Use

### Method 1: Train with CLI (Simplest)
```bash
python cli_app.py train --data-file data/historical_matches.csv
```

**Output:**
```
✅ Loaded 88 samples
✅ Model trained. Accuracy: 94.44%
✅ Model saved to models/sports_model.pkl
```

---

### Method 2: Train with Python Script
```bash
python train_example.py
```

**What it does:**
- Loads 100 match records
- Trains RandomForest model
- Shows accuracy (94.44%)
- Displays feature importance
- Makes sample predictions

---

### Method 3: Train with Custom Code
```python
from src.predictor import get_model_manager
import pandas as pd

# Load your CSV data
df = pd.read_csv('data/historical_matches.csv')

# Initialize model manager
manager = get_model_manager()

# Train model
metrics = manager.train(
    df,
    target_col='home_win',
    model_name='my_custom_model'
)

# Check results
print(f"Accuracy: {metrics['accuracy']:.2%}")
```

---

## 📋 CSV Data Structure

### File Content

**File**: `data/historical_matches.csv`

**Columns** (12 total):
1. `date` - Match date (YYYY-MM-DD format)
2. `home_team` - Home team name
3. `away_team` - Away team name
4. `home_form` - Home team form (0.0-1.0)
5. `away_form` - Away team form (0.0-1.0)
6. `home_advantage` - Home advantage factor (0.0-1.0)
7. `recent_goals` - Recent goals by home team (0-5+)
8. `home_shots_on_target` - Home shots on target (0-15+)
9. `away_shots_on_target` - Away shots on target (0-15+)
10. `home_possession` - Home possession % (0-100)
11. `away_possession` - Away possession % (0-100)
12. `home_win` - Target: 1=home win, 0=other

### Sample Data
```
date,home_team,away_team,home_form,away_form,home_advantage,recent_goals,home_shots_on_target,away_shots_on_target,home_possession,away_possession,home_win
2024-09-01,Arsenal,Liverpool,0.75,0.72,0.55,2,8,6,55,45,1
2024-09-01,Manchester United,Chelsea,0.68,0.70,0.52,1,7,7,52,48,0
2024-09-01,Liverpool,Tottenham,0.80,0.65,0.55,3,9,5,58,42,1
```

---

## 🎯 Using the Data for Model Training

### Step 1: Verify Data Quality
```bash
# Check if CSV is readable
python -c "
import pandas as pd
df = pd.read_csv('data/historical_matches.csv')
print(f'Records: {len(df)}')
print(f'Missing: {df.isnull().sum().sum()}')
print('✅ Data OK')
"
```

### Step 2: Train Model
```bash
# Option A: CLI (recommended)
python cli_app.py train --data-file data/historical_matches.csv

# Option B: Python script
python train_example.py

# Option C: Custom model name
python cli_app.py train --data-file data/historical_matches.csv --model-name my_model_v1
```

### Step 3: Make Predictions
```bash
# Use trained model
python cli_app.py predict --model-name sports_model 0.7 0.6 0.5 2 8 5 62 38
```

---

## 💾 Database Setup Options

### Option 1: Use CSV as Is (Simplest)
```python
import pandas as pd

# Load CSV directly
df = pd.read_csv('data/historical_matches.csv')

# Train model
from src.predictor import get_model_manager
manager = get_model_manager()
manager.train(df, target_col='home_win')
```

**Pros**: No setup, immediate use  
**Cons**: Only 100 records

---

### Option 2: Add More Data to CSV

Create a new CSV with additional matches:
```python
import pandas as pd

# Load existing data
df = pd.read_csv('data/historical_matches.csv')

# Add new rows
new_matches = pd.DataFrame([
    ['2024-10-01', 'Team A', 'Team B', 0.7, 0.6, 0.55, 2, 8, 6, 55, 45, 1],
    ['2024-10-01', 'Team C', 'Team D', 0.65, 0.65, 0.52, 1, 7, 7, 50, 50, 0],
], columns=df.columns)

# Combine
combined = pd.concat([df, new_matches], ignore_index=True)

# Save
combined.to_csv('data/historical_matches_extended.csv', index=False)
```

Then train:
```bash
python cli_app.py train --data-file data/historical_matches_extended.csv
```

---

### Option 3: Use Live API Data

Fetch live data and merge with CSV:
```python
from src.data_fetch import SportsDataFetcher
import pandas as pd

# Load existing CSV
df_csv = pd.read_csv('data/historical_matches.csv')

# Fetch live data
fetcher = SportsDataFetcher()
fixtures = fetcher.get_fixtures(league='39', season='2024')
df_live = fetcher.get_fixtures_as_dataframe(league='39')

# Combine if compatible
combined = pd.concat([df_csv, df_live], ignore_index=True)

# Save
combined.to_csv('data/combined_matches.csv', index=False)

# Train
from src.predictor import get_model_manager
manager = get_model_manager()
manager.train(combined, target_col='home_win', model_name='combined_model')
```

---

## 📊 Feature Explanation

### What Each Feature Means

**Form Scores (0.0-1.0)**
- 0.0-0.3: Poor performance
- 0.3-0.6: Average performance
- 0.6-0.8: Good performance
- 0.8-1.0: Excellent performance

**Home Advantage (0.0-1.0)**
- Typically 0.45-0.60 for soccer
- Varies by league, crowd, etc.

**Shots on Target**
- Higher = more attacking play
- Typical range: 3-15 per team

**Possession %**
- Higher = more control
- Typical range: 35-65 for each team

**Target Variable (home_win)**
- 1 = Home team won
- 0 = Away team won or draw

---

## 🎯 Training Process

### What Happens When You Train

1. **Load CSV Data** (88 matches)
   ```
   ✅ Loaded 88 samples from data/historical_matches.csv
   ```

2. **Auto-select Features** (numeric only)
   ```
   Features selected: home_form, away_form, home_advantage, 
                      recent_goals, shots_on_target, possession
   ```

3. **Split Data**
   ```
   Training set: 70 samples (80%)
   Test set: 18 samples (20%)
   ```

4. **Train RandomForest Model**
   ```
   Trees: 100
   Max depth: automatic
   ```

5. **Evaluate Accuracy**
   ```
   Accuracy:  94.44%
   Precision: 95.00%
   Recall:    94.44%
   F1 Score:  94.43%
   ```

6. **Save Model**
   ```
   ✅ Model saved to models/sports_model.pkl
   ```

---

## 🚀 Next Steps After Training

### Make Predictions
```bash
# Predict for a specific match
python cli_app.py predict --model-name sports_model 0.7 0.6 0.5 2 8 5 62 38

# Outputs:
# class_0_prob: 27.00%  (Away/Draw)
# class_1_prob: 73.00%  (Home Win)
```

### Use Web Dashboard
```bash
streamlit run web_app.py
# Open browser to http://localhost:8501
```

### Analyze Value Bets
```python
from src.predictor import BetAnalyzer

analyzer = BetAnalyzer()
value_bet = analyzer.find_value_bets(
    prediction_probs={'home_win': 0.73},
    odds={'home_win': 1.8}
)
```

---

## 📈 Improving Model Accuracy

### Low Accuracy? Try These:

1. **Add More Data**
   ```bash
   # Current: 100 matches
   # Target: 300-500 matches
   # Expected improvement: +5-15% accuracy
   ```

2. **Better Features**
   ```
   Current: Basic stats
   Add: xG, team strength, injuries, weather
   Expected improvement: +10-20% accuracy
   ```

3. **Feature Engineering**
   ```python
   # Add derived features
   df['form_diff'] = df['home_form'] - df['away_form']
   df['shots_ratio'] = df['home_shots_on_target'] / (df['away_shots_on_target'] + 1)
   df['possession_diff'] = df['home_possession'] - df['away_possession']
   ```

4. **Different Algorithm**
   ```
   Current: RandomForest
   Try: XGBoost, LightGBM, Neural Networks
   Expected improvement: +5-10% accuracy
   ```

---

## ✅ Complete Example Workflow

```bash
# Step 1: Train on CSV
python cli_app.py train --data-file data/historical_matches.csv

# Step 2: Make predictions
python cli_app.py predict --model-name sports_model 0.75 0.70 0.55 2 9 5 60 40

# Step 3: Use web dashboard
streamlit run web_app.py

# Step 4: Analyze with Python
python -c "
from src.predictor import get_model_manager
manager = get_model_manager()
manager.load('sports_model')
result = manager.predict([0.75, 0.70, 0.55, 2, 9, 5, 60, 40])
print(f'Home win probability: {result[\"class_1_prob\"]:.1%}')
"
```

---

## 📚 Additional Resources

- **CSV Guide**: `data/DATA_GUIDE.md`
- **Quick Start**: `QUICKSTART.md`
- **Full Setup**: `SETUP_GUIDE.md`
- **API Reference**: `docs/API_REFERENCE.md`

---

**Your data is ready! Start training: `python cli_app.py train --data-file data/historical_matches.csv`**
