"""Tests for data_fetch module."""

import pytest
from src.data_fetch import SportsDataFetcher, APIClient


class TestAPIClient:
    """Test API client functionality."""

    def test_client_initialization(self):
        """Test client initializes correctly."""
        client = APIClient(timeout=5, max_retries=2)
        assert client.timeout == 5
        assert client.max_retries == 2

    def test_session_creation(self):
        """Test session is created properly."""
        client = APIClient()
        assert client.session is not None


class TestSportsDataFetcher:
    """Test sports data fetcher."""

    def test_fetcher_initialization(self):
        """Test fetcher initializes correctly."""
        fetcher = SportsDataFetcher()
        assert fetcher.api_client is not None
        assert fetcher._cache == {}

    def test_cache_key_generation(self):
        """Test cache key generation."""
        key = SportsDataFetcher._get_cache_key("test", "arg1", "arg2")
        assert "test" in key
        assert "arg1" in key

    def test_cache_operations(self, sample_data):
        """Test cache set and get."""
        fetcher = SportsDataFetcher()
        key = "test_key"
        
        # Set cache
        fetcher._set_cache(key, sample_data)
        
        # Get cache (with timeout override for test)
        cached = fetcher._get_cached(key, ttl=1000)
        assert cached is not None
        assert len(cached) == len(sample_data)

    def test_cache_expiration(self):
        """Test cache expiration."""
        fetcher = SportsDataFetcher()
        key = "test_key"
        
        # Set cache with short TTL
        fetcher._cache[key] = ({"data": "test"}, 0)  # timestamp = 0
        
        # Try to get with short TTL (should be expired)
        result = fetcher._get_cached(key, ttl=1)
        assert result is None

    def test_clear_cache(self, sample_data):
        """Test cache clearing."""
        fetcher = SportsDataFetcher()
        fetcher._set_cache("key1", sample_data)
        fetcher._set_cache("key2", sample_data)
        
        assert len(fetcher._cache) > 0
        
        fetcher.clear_cache()
        assert len(fetcher._cache) == 0
