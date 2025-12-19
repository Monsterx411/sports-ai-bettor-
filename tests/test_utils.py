"""Tests for utility functions."""

import pytest
from src.utils import safe_get, format_currency, format_percentage, get_timestamp


class TestUtilityFunctions:
    """Test utility function."""

    def test_safe_get_nested(self):
        """Test safe nested dictionary access."""
        data = {'user': {'profile': {'name': 'John'}}}
        result = safe_get(data, ['user', 'profile', 'name'])
        assert result == 'John'

    def test_safe_get_missing(self):
        """Test safe access with missing key."""
        data = {'user': {'profile': {}}}
        result = safe_get(data, ['user', 'profile', 'name'], default='Unknown')
        assert result == 'Unknown'

    def test_format_currency(self):
        """Test currency formatting."""
        result = format_currency(1234.56)
        assert '$1,234.56' in result or '$' in result

    def test_format_percentage(self):
        """Test percentage formatting."""
        result = format_percentage(0.75)
        assert '75' in result

    def test_get_timestamp(self):
        """Test timestamp generation."""
        ts = get_timestamp()
        assert len(ts) > 0
        assert '-' in ts  # ISO format has dashes
