#!/bin/bash

# ========================================
# Sports AI Bettor - Complete Setup Script
# ========================================
# This script sets up the entire project environment
# for development with API data fetching enabled

set -e  # Exit on error

echo ""
echo "=================================================="
echo "🎯 Sports AI Bettor - Complete Setup"
echo "=================================================="
echo ""

# ========================================
# Step 1: Check Python
# ========================================
echo "📋 Step 1: Checking Python installation..."
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# ========================================
# Step 2: Create Virtual Environment (Optional)
# ========================================
echo "📋 Step 2: Python Environment"
echo "✅ Using system Python 3.14"
echo ""

# ========================================
# Step 3: Upgrade pip and install setuptools
# ========================================
echo "📋 Step 3: Updating pip and setuptools..."
python -m pip install --upgrade pip setuptools wheel --break-system-packages 2>/dev/null || python -m pip install --upgrade pip setuptools wheel
echo "✅ pip and setuptools updated"
echo ""

# ========================================
# Step 4: Install project dependencies
# ========================================
echo "📋 Step 4: Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt --break-system-packages 2>/dev/null || python -m pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi
echo ""

# ========================================
# Step 5: Check and configure .env file
# ========================================
echo "📋 Step 5: Environment Configuration"

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from template"
    else
        echo "⚠️  .env.example not found. Creating basic .env..."
        cat > .env << 'EOF'
API_SPORTS_KEY=YOUR_API_SPORTS_KEY_HERE
ODDS_API_KEY=YOUR_ODDS_API_KEY_HERE
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
DEFAULT_SPORT=soccer
EDGE_THRESHOLD=0.05
MIN_CONFIDENCE=0.6
RANDOM_FOREST_ESTIMATORS=100
TEST_SIZE=0.2
RANDOM_STATE=42
REQUEST_TIMEOUT=10
MAX_RETRIES=3
RETRY_BACKOFF=1.5
CACHE_ENABLED=true
CACHE_TTL=3600
EOF
        echo "✅ .env file created"
    fi
else
    echo "✅ .env file already exists"
fi
echo ""

# ========================================
# Step 6: Create necessary directories
# ========================================
echo "📋 Step 6: Creating project directories..."
mkdir -p data models logs config src tests docs
echo "✅ Project directories created"
echo ""

# ========================================
# Step 7: Test imports and configuration
# ========================================
echo "📋 Step 7: Testing Python imports..."
python << 'PYEOF'
import sys
try:
    import pandas
    import numpy
    import sklearn
    import requests
    import streamlit
    import click
    print("✅ All core dependencies imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
PYEOF
echo ""

# ========================================
# Step 8: Load environment and test API client
# ========================================
echo "📋 Step 8: Testing data fetching setup..."
python << 'PYEOF'
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Environment variables loaded from .env")
else:
    print("⚠️  .env file not found")

# Test API configuration
api_sports_key = os.getenv('API_SPORTS_KEY', 'NOT_SET')
odds_api_key = os.getenv('ODDS_API_KEY', 'NOT_SET')

if api_sports_key == 'YOUR_API_SPORTS_KEY_HERE' or api_sports_key == 'NOT_SET':
    print("⚠️  API_SPORTS_KEY not configured. Set your key in .env")
else:
    print(f"✅ API_SPORTS_KEY configured (starts with: {api_sports_key[:10]}...)")

if odds_api_key == 'YOUR_ODDS_API_KEY_HERE' or odds_api_key == 'NOT_SET':
    print("⚠️  ODDS_API_KEY not configured. Set your key in .env")
else:
    print(f"✅ ODDS_API_KEY configured (starts with: {odds_api_key[:10]}...)")

# Test config module
try:
    from config.settings import settings
    print("✅ Config module loaded successfully")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   Log Level: {settings.LOG_LEVEL}")
except Exception as e:
    print(f"❌ Failed to load config: {e}")

PYEOF
echo ""

# ========================================
# Step 9: Display data fetching options
# ========================================
echo "📋 Step 9: Data Fetching Options"
echo ""
echo "Your project supports multiple data sources:"
echo ""
echo "1️⃣  CSV File (No API needed)"
echo "   Location: data/historical_matches.csv"
echo "   Usage: python train_example.py"
echo ""
echo "2️⃣  API Sports (Live data)"
echo "   - Get free key: https://www.api-football.com/"
echo "   - Add to .env: API_SPORTS_KEY=your_key_here"
echo "   - Test with: python src/data_fetch.py"
echo ""
echo "3️⃣  The Odds API (Betting odds)"
echo "   - Get free key: https://theoddsapi.com/"
echo "   - Add to .env: ODDS_API_KEY=your_key_here"
echo ""
echo "Current CSV Status:"
if [ -f "data/historical_matches.csv" ]; then
    CSV_ROWS=$(wc -l < data/historical_matches.csv)
    echo "   ✅ CSV found with $((CSV_ROWS - 1)) match records"
else
    echo "   ⚠️  CSV not found - create with train_example.py"
fi
echo ""

# ========================================
# Step 10: Summary and next steps
# ========================================
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Configure API Keys (Optional)"
echo "   Edit .env and add your API keys:"
echo "   - API_SPORTS_KEY=your_key"
echo "   - ODDS_API_KEY=your_key"
echo ""
echo "2. Test Training with CSV Data"
echo "   python train_example.py"
echo ""
echo "3. Use the CLI for Predictions"
echo "   python cli_app.py --help"
echo ""
echo "4. Start Web Dashboard"
echo "   streamlit run web_app.py"
echo ""
echo "5. Fetch Live Data (with API keys)"
echo "   python src/data_fetch.py"
echo ""
echo "📖 Documentation:"
echo "   - README.md - Project overview"
echo "   - docs/ - Detailed documentation"
echo "   - data/DATA_GUIDE.md - Data format guide"
echo ""
echo "💡 Useful Commands:"
echo "   Train model:        python train_example.py"
echo "   Make prediction:    python cli_app.py predict --help"
echo "   Web dashboard:      streamlit run web_app.py"
echo "   Run tests:          pytest tests/"
echo "   Check code style:   flake8 src/ config/ cli_app.py web_app.py"
echo ""
echo "=================================================="
echo ""
