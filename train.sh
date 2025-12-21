#!/bin/bash

# 🎯 Sports AI Bettor - Training Guide
# This script shows how to train the model with the historical data

echo "================================================"
echo "🎯 Sports AI Bettor - Model Training Guide"
echo "================================================"
echo ""

# Step 1: Check if data file exists
if [ -f "data/historical_matches.csv" ]; then
    echo "✅ Step 1: Data file found!"
    echo "   Location: data/historical_matches.csv"
    echo "   Size: $(wc -l < data/historical_matches.csv) lines"
    echo ""
else
    echo "❌ Error: historical_matches.csv not found"
    exit 1
fi

# Step 2: Show file structure
echo "📋 Step 2: Data structure"
echo "   Columns: date, home_team, away_team, home_form, away_form,"
echo "            home_advantage, recent_goals, home_shots_on_target,"
echo "            away_shots_on_target, home_possession, away_possession, home_win"
echo ""
echo "   Sample rows:"
head -3 data/historical_matches.csv | tail -2 | sed 's/^/   /'
echo ""

# Step 3: Training options
echo "🤖 Step 3: Training options"
echo ""
echo "   OPTION A: Using Example Script (Recommended)"
echo "   ✨ Shows full training process with metrics and predictions"
echo "   Command:"
echo "      python train_example.py"
echo ""
echo "   OPTION B: Using CLI"
echo "   Command:"
echo "      python cli_app.py train --data-file data/historical_matches.csv"
echo ""
echo "   OPTION C: Using Python Code"
echo "   Example:"
echo "      from src.predictor import get_model_manager"
echo "      import pandas as pd"
echo "      df = pd.read_csv('data/historical_matches.csv')"
echo "      manager = get_model_manager()"
echo "      metrics = manager.train(df)"
echo ""

# Step 4: Verify dependencies
echo "✅ Step 4: Checking dependencies..."
python -c "import pandas; import sklearn" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ All dependencies installed"
else
    echo "   ⚠️  Installing dependencies..."
    pip install -q -r requirements.txt
    echo "   ✅ Dependencies installed"
fi
echo ""

# Step 5: Ready to train
echo "🚀 Step 5: Ready to train!"
echo ""
echo "   Run one of the commands above to start training."
echo "   Example:"
echo "      python train_example.py"
echo ""
echo "================================================"
echo "📚 For more information, see data/DATA_GUIDE.md"
echo "================================================"
