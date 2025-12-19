"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path
from config.settings import LOGS_DIR, settings


def setup_logger(
    name: str,
    level: str = None,
    log_file: bool = True
) -> logging.Logger:
    """
    Setup a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (uses settings.LOG_LEVEL if not provided)
        log_file: Whether to write to file
        
    Returns:
        Configured logger instance
    """
    level = level or settings.LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file_path = LOGS_DIR / f"{name.replace('.', '_')}.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
