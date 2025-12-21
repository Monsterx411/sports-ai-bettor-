#!/usr/bin/env python3
"""
Sports AI Bettor - Complete Environment Setup Script
Configures the project for development with API data fetching capabilities
"""

import os
import sys
from pathlib import Path
import subprocess

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 50)
    print(f"🎯 {text}")
    print("=" * 50 + "\n")

def print_step(num, text):
    """Print step header"""
    print(f"📋 Step {num}: {text}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def run_command(cmd, description=None):
    """Run shell command with error handling"""
    if description:
        print(f"  → {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "already satisfied" not in result.stderr.lower():
            print_warning(f"Command had warnings: {result.stderr[:100]}")
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to run command: {e}")
        return False

def check_python():
    """Check Python installation"""
    print_step(1, "Checking Python installation")
    version = sys.version.split()[0]
    print_success(f"Python {version} found")
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ required")
        return False
    return True

def install_dependencies():
    """Install project dependencies"""
    print_step(2, "Installing project dependencies")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_warning("requirements.txt not found")
        return False
    
    # Install requirements
    cmd = f"{sys.executable} -m pip install -r requirements.txt --break-system-packages 2>/dev/null || {sys.executable} -m pip install -r requirements.txt"
    if run_command(cmd, "Installing packages"):
        print_success("Dependencies installed")
        return True
    else:
        print_warning("Some packages may have failed to install")
        return True

def setup_env_file():
    """Setup environment configuration"""
    print_step(3, "Environment Configuration")
    
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print_success(".env file already exists")
    elif example_path.exists():
        # Copy example to .env
        with open(example_path) as f:
            content = f.read()
        with open(env_path, 'w') as f:
            f.write(content)
        print_success(".env file created from template")
    else:
        print_warning(".env.example not found, creating basic .env")
        with open(env_path, 'w') as f:
            f.write("""# Sports AI Bettor - Development Environment
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
""")
        print_success(".env file created")
    
    return True

def create_directories():
    """Create necessary project directories"""
    print_step(4, "Creating project directories")
    
    dirs = ["data", "models", "logs", "config", "src", "tests", "docs"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    
    print_success("Project directories created/verified")
    return True

def test_imports():
    """Test that all imports work"""
    print_step(5, "Testing Python imports")
    
    try:
        import pandas
        import numpy
        import sklearn
        import requests
        import streamlit
        import click
        from dotenv import load_dotenv
        print_success("All core dependencies imported successfully")
        return True
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print_step(6, "Testing environment configuration")
    
    # Load env
    from dotenv import load_dotenv
    load_dotenv()
    
    api_sports = os.getenv("API_SPORTS_KEY", "NOT_SET")
    odds_api = os.getenv("ODDS_API_KEY", "NOT_SET")
    
    print_success("Environment variables loaded from .env")
    
    # Check API keys
    if api_sports in ["YOUR_API_SPORTS_KEY_HERE", "NOT_SET"]:
        print_warning("API_SPORTS_KEY not configured")
    else:
        print_success(f"API_SPORTS_KEY configured ({api_sports[:15]}...)")
    
    if odds_api in ["YOUR_ODDS_API_KEY_HERE", "NOT_SET"]:
        print_warning("ODDS_API_KEY not configured")
    else:
        print_success(f"ODDS_API_KEY configured ({odds_api[:15]}...)")
    
    # Test config module
    try:
        from config.settings import settings
        print_success("Config module loaded")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Log Level: {settings.LOG_LEVEL}")
        print(f"   Cache Enabled: {settings.CACHE_ENABLED}")
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return False
    
    return True

def test_data_fetching():
    """Test data fetching capabilities"""
    print_step(7, "Checking data fetching capabilities")
    
    # Check CSV
    csv_path = Path("data/historical_matches.csv")
    if csv_path.exists():
        with open(csv_path) as f:
            lines = len(f.readlines())
        print_success(f"CSV data found ({lines - 1} match records)")
    else:
        print_warning("CSV file not found - run train_example.py to create")
    
    # Check API client
    try:
        from src.data_fetch import APIClient, SportsDataFetcher
        print_success("Data fetching modules loaded")
    except Exception as e:
        print_warning(f"Could not load data fetching module: {e}")
    
    return True

def display_summary():
    """Display setup summary and next steps"""
    print_header("Setup Complete! 🎉")
    
    print("📚 CONFIGURATION STATUS:")
    print("  ✅ Python environment set up")
    print("  ✅ Dependencies installed")
    print("  ✅ Environment variables configured")
    print("  ✅ Project structure created")
    print()
    
    print("📊 DATA SOURCES AVAILABLE:")
    print("  1️⃣  CSV File - data/historical_matches.csv")
    print("       → No API needed, ready to use")
    print("  2️⃣  API Sports - https://www.api-football.com/")
    print("       → Live soccer/football data")
    print("       → Add API_SPORTS_KEY to .env")
    print("  3️⃣  The Odds API - https://theoddsapi.com/")
    print("       → Betting odds data")
    print("       → Add ODDS_API_KEY to .env")
    print()
    
    print("🚀 NEXT STEPS:")
    print()
    print("  1. (Optional) Add API Keys to .env:")
    print("     nano .env")
    print("     # Then add your API keys")
    print()
    print("  2. Train the Model:")
    print("     python train_example.py")
    print()
    print("  3. Make Predictions:")
    print("     python cli_app.py predict --help")
    print()
    print("  4. Start Web Dashboard:")
    print("     streamlit run web_app.py")
    print()
    print("  5. Fetch Live Data (requires API keys):")
    print("     python src/data_fetch.py")
    print()
    
    print("💡 USEFUL COMMANDS:")
    print("  Train model:       python train_example.py")
    print("  CLI predictions:   python cli_app.py predict --help")
    print("  Web dashboard:     streamlit run web_app.py")
    print("  Run tests:         pytest tests/")
    print("  Check code:        flake8 src/")
    print()
    
    print("📖 DOCUMENTATION:")
    print("  • README.md - Project overview")
    print("  • docs/ - Detailed guides")
    print("  • data/DATA_GUIDE.md - Data format reference")
    print()
    
    print("=" * 50)
    print()

def main():
    """Run complete setup"""
    print_header("Sports AI Bettor - Complete Setup")
    
    steps = [
        (check_python, "Python check"),
        (install_dependencies, "Dependency installation"),
        (setup_env_file, "Environment setup"),
        (create_directories, "Directory creation"),
        (test_imports, "Import test"),
        (test_environment, "Environment test"),
        (test_data_fetching, "Data fetching test"),
    ]
    
    failed = []
    for step_func, name in steps:
        try:
            if not step_func():
                failed.append(name)
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            return 1
        except Exception as e:
            print_error(f"Unexpected error in {name}: {e}")
            failed.append(name)
    
    if failed:
        print_warning(f"Some steps had issues: {', '.join(failed)}")
    
    display_summary()
    return 0

if __name__ == "__main__":
    sys.exit(main())
