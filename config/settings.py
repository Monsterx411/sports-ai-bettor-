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
    RANDOM_FOREST_ESTIMATORS: int = int(os.getenv("RANDOM_FOREST_ESTIMATORS", "100"))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))
    USE_ADVANCED_TRAINING: bool = os.getenv("USE_ADVANCED_TRAINING", "true").lower() == "true"
    CV_FOLDS: int = int(os.getenv("CV_FOLDS", "5"))

    # Daily Predictions
    MIN_DAILY_MATCHES: int = int(os.getenv("MIN_DAILY_MATCHES", "10"))
    TOP_SPORTS: str = os.getenv("TOP_SPORTS", "soccer,basketball")

    # API Settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "1.5"))

    # Cache Settings
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour in seconds

    # Database/Storage (for future use)
    DB_URL: Optional[str] = os.getenv("DATABASE_URL", None)

    @classmethod
    def validate(cls) -> bool:
        """Validate critical settings."""
        if cls.API_SPORTS_KEY == "YOUR_API_SPORTS_KEY":
            print("⚠️  Warning: API_SPORTS_KEY not set. Set environment variables for production.")
        if cls.ODDS_API_KEY == "YOUR_ODDS_API_KEY":
            print("⚠️  Warning: ODDS_API_KEY not set. Set environment variables for production.")
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
