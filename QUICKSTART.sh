#!/bin/bash
# Quick Start Guide for Sports AI Bettor

echo "🎯 Sports AI Bettor - Quick Start"
echo "=================================="
echo ""

# Step 1: Install dependencies
echo "📦 Step 1: Installing dependencies..."
echo "Run: pip install -r requirements.txt"
echo ""

# Step 2: Configure environment
echo "⚙️  Step 2: Setting up environment..."
echo "Run: cp .env.example .env"
echo "Then edit .env with your API keys:"
echo "  - API_SPORTS_KEY"
echo "  - ODDS_API_KEY"
echo ""

# Step 3: Prepare data
echo "📊 Step 3: Prepare training data..."
echo "Create: data/historical.csv with columns:"
echo "  - home_team, away_team, date"
echo "  - Features: home_form, away_form, home_advantage, etc."
echo "  - Target: home_win (0 or 1)"
echo ""

# Step 4: Train model
echo "🤖 Step 4: Train the model..."
echo "Run: python cli_app.py train --data-file data/historical.csv"
echo ""

# Step 5: Make predictions
echo "🔮 Step 5: Make predictions..."
echo "Option A (CLI):"
echo "  python cli_app.py predict --model-name sports_model --features 0.7 0.6 0.5"
echo ""
echo "Option B (Web Dashboard):"
echo "  streamlit run web_app.py"
echo ""

# Step 6: Analyze value bets
echo "💰 Step 6: Find value bets..."
echo "Run: python cli_app.py analyze --event-id 123 \\
    --odds Home 1.80 --odds Away 2.50 --odds Draw 3.50"
echo ""

echo "📚 For detailed documentation, see:"
echo "  - README.md"
echo "  - ENHANCEMENT_SUMMARY.md"
echo "  - docs/API_REFERENCE.md"
echo "  - docs/ADVANCED_USAGE.md"
echo ""

echo "✅ Setup complete!"
