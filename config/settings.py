"""
Configuration management for Sports AI Bettor.
Handles environment variables, API keys, and application settings.
"""

import os
from pathlib import Path
from typing import Optional

# Base directories
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create necessary directories
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


class Settings:
    """Application settings with environment variable fallbacks."""

    # API Keys
    API_SPORTS_KEY: str = os.getenv("API_SPORTS_KEY", "YOUR_API_SPORTS_KEY")
    ODDS_API_KEY: str = os.getenv("ODDS_API_KEY", "YOUR_ODDS_API_KEY")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Sports Betting Parameters
    DEFAULT_SPORT: str = os.getenv("DEFAULT_SPORT", "soccer")
    EDGE_THRESHOLD: float = float(os.getenv("EDGE_THRESHOLD", "0.05"))  # 5% minimum edge
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE", "0.6"))
    
    # Model Settings
    RANDOM_FOREST_ESTIMATORS: int = int(os.getenv("RANDOM_FOREST_ESTIMATORS", "200"))
    GRADIENT_BOOSTING_ESTIMATORS: int = int(os.getenv("GRADIENT_BOOSTING_ESTIMATORS", "200"))
    RF_MAX_DEPTH: int = int(os.getenv("RF_MAX_DEPTH", "20"))
    GB_MAX_DEPTH: int = int(os.getenv("GB_MAX_DEPTH", "7"))
    GB_LEARNING_RATE: float = float(os.getenv("GB_LEARNING_RATE", "0.05"))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))
    MODEL_ENSEMBLE_VOTING: str = os.getenv("MODEL_ENSEMBLE_VOTING", "soft")  # 'soft' or 'hard'

    # API Settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "1.5"))

    # Cache Settings
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour in seconds
    
    # Data Settings
    DEFAULT_DATASET: str = os.getenv("DEFAULT_DATASET", "data/enhanced_training_dataset.csv")
    TARGET_COLUMN: str = os.getenv("TARGET_COLUMN", "home_win")
    EXPECTED_FEATURES: int = int(os.getenv("EXPECTED_FEATURES", "12"))
    
    # Bankroll Management (Kelly Criterion)
    KELLY_CRITERION: float = float(os.getenv("KELLY_CRITERION", "0.25"))  # Conservative 25% Kelly
    MAX_BET_SIZE: float = float(os.getenv("MAX_BET_SIZE", "100"))  # Max bet per wager
    INITIAL_BANKROLL: float = float(os.getenv("INITIAL_BANKROLL", "1000"))  # Starting bankroll

    @classmethod
    def validate(cls) -> bool:
        """Validate critical settings."""
        warnings = []
        
        if cls.API_SPORTS_KEY == "YOUR_API_SPORTS_KEY":
            warnings.append("⚠️  API_SPORTS_KEY not set")
        if cls.ODDS_API_KEY == "YOUR_ODDS_API_KEY":
            warnings.append("⚠️  ODDS_API_KEY not set")
        
        # Validate ranges
        if not (0 <= cls.EDGE_THRESHOLD <= 1):
            warnings.append(f"⚠️  EDGE_THRESHOLD must be 0-1, got {cls.EDGE_THRESHOLD}")
        if not (0 <= cls.MIN_CONFIDENCE <= 1):
            warnings.append(f"⚠️  MIN_CONFIDENCE must be 0-1, got {cls.MIN_CONFIDENCE}")
        if not (0 <= cls.KELLY_CRITERION <= 1):
            warnings.append(f"⚠️  KELLY_CRITERION must be 0-1, got {cls.KELLY_CRITERION}")
        
        for warning in warnings:
            print(warning)
        
        return True

    @classmethod
    def to_dict(cls) -> dict:
        """Export settings as dictionary."""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }


# Initialize settings
settings = Settings()
settings.validate()
