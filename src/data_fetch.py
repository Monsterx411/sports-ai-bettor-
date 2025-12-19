"""
Data fetching module for sports APIs.
Handles fixture data and odds retrieval with caching, retries, and error handling.
"""

import time
from functools import lru_cache
from typing import Dict, List, Optional, Any
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from src.logger import setup_logger

logger = setup_logger(__name__)


class APIClient:
    """Robust API client with retry logic and caching."""

    def __init__(self, timeout: int = None, max_retries: int = None):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=settings.RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get(self, url: str, headers: Dict[str, str] = None, **kwargs) -> Optional[Dict]:
        """
        Perform GET request with error handling.
        
        Args:
            url: Request URL
            headers: Request headers
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            JSON response or None on error
        """
        try:
            logger.debug(f"Fetching: {url}")
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None


class SportsDataFetcher:
    """Fetch sports data from APIs with caching."""

    def __init__(self):
        """Initialize fetcher with API client."""
        self.api_client = APIClient()
        self._cache = {}

    @staticmethod
    def _get_cache_key(func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments."""
        return f"{func_name}_{args}_{sorted(kwargs.items())}"

    def _get_cached(self, key: str, ttl: int = None) -> Optional[Any]:
        """Get value from cache if not expired."""
        ttl = ttl or settings.CACHE_TTL
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < ttl:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Store value in cache."""
        if settings.CACHE_ENABLED:
            self._cache[key] = (value, time.time())

    def fetch_fixtures(
        self,
        sport: str = "soccer",
        league: str = "premier_league",
        season: int = 2025
    ) -> pd.DataFrame:
        """
        Fetch upcoming fixtures from API.
        
        Args:
            sport: Sport type (default: soccer)
            league: League identifier
            season: Season year
            
        Returns:
            DataFrame with fixture data
        """
        cache_key = self._get_cache_key("fixtures", sport, league, season)
        
        # Check cache
        if settings.CACHE_ENABLED:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        url = f"https://api.api-sports.io/v3/fixtures"
        params = {
            "league": league,
            "season": season,
            "status": "NOT_STARTED"
        }
        headers = {"x-apisports-key": settings.API_SPORTS_KEY}

        data = self.api_client.get(url, headers=headers, params=params)
        
        if not data or "response" not in data:
            logger.warning(f"No fixtures data returned for {league}")
            return pd.DataFrame()

        try:
            fixtures = []
            for fixture in data.get("response", []):
                fixtures.append({
                    "fixture_id": fixture.get("id"),
                    "date": fixture.get("fixture", {}).get("date"),
                    "status": fixture.get("fixture", {}).get("status"),
                    "home_team": fixture.get("teams", {}).get("home", {}).get("name"),
                    "away_team": fixture.get("teams", {}).get("away", {}).get("name"),
                    "home_team_id": fixture.get("teams", {}).get("home", {}).get("id"),
                    "away_team_id": fixture.get("teams", {}).get("away", {}).get("id"),
                })
            
            df = pd.DataFrame(fixtures)
            logger.info(f"Fetched {len(df)} fixtures for {league}")
            self._set_cache(cache_key, df)
            return df
            
        except Exception as e:
            logger.error(f"Error parsing fixtures: {e}")
            return pd.DataFrame()

    def fetch_odds(self, event_id: str, region: str = "us") -> Dict[str, float]:
        """
        Fetch betting odds for a specific event.
        
        Args:
            event_id: Unique event identifier
            region: Region code for odds
            
        Returns:
            Dictionary with odds for different outcomes
        """
        cache_key = self._get_cache_key("odds", event_id, region)
        
        # Check cache
        if settings.CACHE_ENABLED:
            cached = self._get_cached(cache_key, ttl=1800)  # 30 min TTL for odds
            if cached is not None:
                return cached

        url = f"https://api.the-odds-api.com/v4/sports/soccer/events/{event_id}/odds"
        params = {
            "apiKey": settings.ODDS_API_KEY,
            "regions": region,
            "markets": "h2h"
        }

        data = self.api_client.get(url, params=params)
        
        if not data or "bookmakers" not in data:
            logger.warning(f"No odds data for event {event_id}")
            return {}

        try:
            odds_dict = {}
            for bookmaker in data.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "unknown")
                        price = outcome.get("price", 0.0)
                        odds_dict[name] = price
            
            logger.debug(f"Fetched odds for event {event_id}: {odds_dict}")
            self._set_cache(cache_key, odds_dict)
            return odds_dict
            
        except Exception as e:
            logger.error(f"Error parsing odds: {e}")
            return {}

    def fetch_team_stats(self, team_id: int, season: int = 2025) -> Dict[str, Any]:
        """
        Fetch team statistics.
        
        Args:
            team_id: Team identifier
            season: Season year
            
        Returns:
            Dictionary with team stats
        """
        cache_key = self._get_cache_key("team_stats", team_id, season)
        
        if settings.CACHE_ENABLED:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        url = f"https://api.api-sports.io/v3/teams/statistics"
        params = {
            "team": team_id,
            "season": season
        }
        headers = {"x-apisports-key": settings.API_SPORTS_KEY}

        data = self.api_client.get(url, headers=headers, params=params)
        
        if not data or "response" not in data:
            logger.warning(f"No stats data for team {team_id}")
            return {}

        try:
            stats = data.get("response", {})
            self._set_cache(cache_key, stats)
            return stats
        except Exception as e:
            logger.error(f"Error parsing team stats: {e}")
            return {}

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        logger.info("Cache cleared")


# Singleton instance
_fetcher = None


def get_fetcher() -> SportsDataFetcher:
    """Get or create fetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = SportsDataFetcher()
    return _fetcher
