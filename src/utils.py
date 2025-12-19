"""Utility functions for the application."""

from typing import Any, Dict, List
import json
from datetime import datetime
from src.logger import setup_logger

logger = setup_logger(__name__)


def safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any:
    """
    Safely get nested dictionary value.
    
    Args:
        dictionary: Dictionary to search
        keys: List of keys to traverse
        default: Default value if not found
        
    Returns:
        Value at nested key path or default
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default


def format_currency(value: float, symbol: str = "$") -> str:
    """Format value as currency."""
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage."""
    return f"{value * 100:.{decimals}f}%"


def export_json(data: Dict, filename: str) -> bool:
    """Export data to JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported data to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        return False


def import_json(filename: str) -> Dict:
    """Import data from JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error importing JSON: {e}")
        return {}


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()
