"""
Live Sports Data Integration Module
Fetches real-time sports data from multiple reliable APIs for betting predictions.
Supports multiple sports: Soccer, Basketball, American Football, etc.
"""

import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class LiveMatch:
    """Live match data structure."""
    match_id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    match_time: datetime
    status: str  # "scheduled", "live", "finished"
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    bookmaker: Optional[str] = None
    confidence: Optional[float] = None


class LiveSportsDataFetcher:
    """
    Main class for fetching live sports data from multiple APIs.
    Provides unified interface for different sports and data sources.
    """

    def __init__(self):
        """Initialize fetcher with API credentials."""
        self.api_sports_key = os.getenv("API_SPORTS_KEY", "demo")
        self.odds_api_key = os.getenv("ODDS_API_KEY", "demo")
        self.session = self._create_session()
        self.last_request_time = {}

    def _create_session(self) -> requests.Session:
        """Create requests session with timeout."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Sports-AI-Bettor/1.0"
        })
        return session

    def _rate_limit(self, endpoint: str, min_interval: float = 1.0) -> None:
        """Simple rate limiting per endpoint."""
        if endpoint in self.last_request_time:
            elapsed = time.time() - self.last_request_time[endpoint]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time[endpoint] = time.time()

    # ==================== SOCCER/FOOTBALL ====================

    def fetch_live_soccer_matches(
        self,
        league: str = "premier_league",
        days_ahead: int = 7
    ) -> List[LiveMatch]:
        """
        Fetch live and upcoming soccer matches.
        
        Args:
            league: League code (e.g., "premier_league", "serie_a", "la_liga")
            days_ahead: Look ahead days
            
        Returns:
            List of LiveMatch objects
        """
        matches = []
        
        # Try multiple data sources
        try:
            matches.extend(self._fetch_soccer_api_sports(league, days_ahead))
        except Exception as e:
            logger.warning(f"API-Sports fetch failed: {e}")
        
        try:
            matches.extend(self._fetch_soccer_odds_api(days_ahead))
        except Exception as e:
            logger.warning(f"Odds API fetch failed: {e}")
        
        # Remove duplicates based on match_id
        seen = set()
        unique_matches = []
        for match in matches:
            if match.match_id not in seen:
                unique_matches.append(match)
                seen.add(match.match_id)
        
        return unique_matches

    def _fetch_soccer_api_sports(
        self,
        league: str,
        days_ahead: int
    ) -> List[LiveMatch]:
        """Fetch from API-Sports.io."""
        self._rate_limit("api-sports")
        
        matches = []
        url = "https://v3.football.api-sports.io/fixtures"
        
        # Map league names to league IDs
        league_ids = {
            "premier_league": 39,
            "serie_a": 135,
            "la_liga": 140,
            "ligue_1": 61,
            "bundesliga": 78,
            "champions_league": 2,
            "europa_league": 3,
        }
        
        league_id = league_ids.get(league, 39)
        
        # Get fixtures for next N days
        now = datetime.utcnow()
        until_date = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        params = {
            "league": league_id,
            "from": now.strftime("%Y-%m-%d"),
            "to": until_date,
            "status": "LIVE,NOT_STARTED,FINISHED"
        }
        
        headers = {"x-apisports-key": self.api_sports_key}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("response"):
                for fixture in data["response"]:
                    match = self._parse_api_sports_fixture(fixture, league)
                    if match:
                        matches.append(match)
        except Exception as e:
            logger.error(f"Error fetching from API-Sports: {e}")
        
        return matches

    def _parse_api_sports_fixture(self, fixture: Dict, league: str) -> Optional[LiveMatch]:
        """Parse API-Sports fixture into LiveMatch object."""
        try:
            match_id = f"apisports_{fixture['fixture']['id']}"
            
            return LiveMatch(
                match_id=match_id,
                sport="soccer",
                league=league,
                home_team=fixture["teams"]["home"]["name"],
                away_team=fixture["teams"]["away"]["name"],
                match_time=datetime.fromisoformat(
                    fixture["fixture"]["date"].replace("Z", "+00:00")
                ),
                status=fixture["fixture"]["status"].lower(),
                home_score=fixture["goals"]["home"],
                away_score=fixture["goals"]["away"],
                bookmaker="api-sports"
            )
        except Exception as e:
            logger.warning(f"Error parsing fixture: {e}")
            return None

    def _fetch_soccer_odds_api(self, days_ahead: int) -> List[LiveMatch]:
        """Fetch from The-Odds-API.com (free tier available)."""
        self._rate_limit("odds-api")
        
        matches = []
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/events"
        
        params = {
            "apiKey": self.odds_api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                for event in data:
                    match = self._parse_odds_api_event(event)
                    if match:
                        matches.append(match)
        except Exception as e:
            logger.error(f"Error fetching from Odds API: {e}")
        
        return matches

    def _parse_odds_api_event(self, event: Dict) -> Optional[LiveMatch]:
        """Parse Odds API event into LiveMatch object."""
        try:
            match_id = f"oddsapi_{event['id']}"
            
            # Extract odds
            odds_dict = {}
            if event.get("bookmakers"):
                for bookmaker in event["bookmakers"]:
                    if bookmaker.get("markets"):
                        for market in bookmaker["markets"]:
                            if market["key"] == "h2h":
                                for outcome in market["outcomes"]:
                                    if outcome["name"] == "Home":
                                        odds_dict["home"] = outcome["price"]
                                    elif outcome["name"] == "Draw":
                                        odds_dict["draw"] = outcome["price"]
                                    elif outcome["name"] == "Away":
                                        odds_dict["away"] = outcome["price"]
                    break  # Use first bookmaker
            
            return LiveMatch(
                match_id=match_id,
                sport="soccer",
                league="epl",
                home_team=event["home_team"],
                away_team=event["away_team"],
                match_time=datetime.fromisoformat(
                    event["commence_time"].replace("Z", "+00:00")
                ),
                status="scheduled",
                odds_home=odds_dict.get("home"),
                odds_draw=odds_dict.get("draw"),
                odds_away=odds_dict.get("away"),
                bookmaker="odds-api"
            )
        except Exception as e:
            logger.warning(f"Error parsing event: {e}")
            return None

    # ==================== BASKETBALL ====================

    def fetch_live_basketball_matches(
        self,
        league: str = "nba",
        days_ahead: int = 7
    ) -> List[LiveMatch]:
        """Fetch live and upcoming basketball matches."""
        self._rate_limit("basketball-api")
        
        matches = []
        url = "https://api.api-sports.io/v3/games"
        
        # Map league codes
        league_ids = {
            "nba": 12,
            "euroleague": 151,
        }
        
        league_id = league_ids.get(league, 12)
        
        now = datetime.utcnow()
        season_year = now.year if now.month >= 10 else now.year - 1
        
        params = {
            "league": league_id,
            "season": season_year
        }
        
        headers = {"x-apisports-key": self.api_sports_key}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("response"):
                for game in data["response"][:100]:  # Limit to 100 most recent
                    match = self._parse_basketball_game(game, league)
                    if match:
                        matches.append(match)
        except Exception as e:
            logger.error(f"Error fetching basketball: {e}")
        
        return matches

    def _parse_basketball_game(self, game: Dict, league: str) -> Optional[LiveMatch]:
        """Parse basketball game into LiveMatch object."""
        try:
            match_id = f"basketball_{game['id']}"
            
            return LiveMatch(
                match_id=match_id,
                sport="basketball",
                league=league,
                home_team=game["teams"]["home"]["name"],
                away_team=game["teams"]["away"]["name"],
                match_time=datetime.fromisoformat(
                    game["date"].replace("Z", "+00:00")
                ),
                status=game["status"].lower(),
                home_score=game["scores"]["home"].get("points") if game["scores"]["home"] else None,
                away_score=game["scores"]["away"].get("points") if game["scores"]["away"] else None,
                bookmaker="api-sports"
            )
        except Exception as e:
            logger.warning(f"Error parsing basketball game: {e}")
            return None

    # ==================== AMERICAN FOOTBALL ====================

    def fetch_live_nfl_matches(self, days_ahead: int = 7) -> List[LiveMatch]:
        """Fetch NFL matches."""
        self._rate_limit("nfl-api")
        
        matches = []
        url = "https://api.api-sports.io/v3/games"
        
        params = {
            "league": 1,  # NFL league ID
            "season": datetime.utcnow().year
        }
        
        headers = {"x-apisports-key": self.api_sports_key}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("response"):
                for game in data["response"][:100]:
                    match = self._parse_nfl_game(game)
                    if match:
                        matches.append(match)
        except Exception as e:
            logger.error(f"Error fetching NFL: {e}")
        
        return matches

    def _parse_nfl_game(self, game: Dict) -> Optional[LiveMatch]:
        """Parse NFL game into LiveMatch object."""
        try:
            match_id = f"nfl_{game['id']}"
            
            return LiveMatch(
                match_id=match_id,
                sport="american_football",
                league="nfl",
                home_team=game["teams"]["home"]["name"],
                away_team=game["teams"]["away"]["name"],
                match_time=datetime.fromisoformat(
                    game["date"].replace("Z", "+00:00")
                ),
                status=game["status"].lower(),
                home_score=game["scores"]["home"].get("points"),
                away_score=game["scores"]["away"].get("points"),
                bookmaker="api-sports"
            )
        except Exception as e:
            logger.warning(f"Error parsing NFL game: {e}")
            return None

    # ==================== UTILITY METHODS ====================

    def to_dataframe(self, matches: List[LiveMatch]) -> pd.DataFrame:
        """Convert LiveMatch objects to pandas DataFrame."""
        data = []
        for match in matches:
            data.append({
                "match_id": match.match_id,
                "sport": match.sport,
                "league": match.league,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_time": match.match_time,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "odds_home": match.odds_home,
                "odds_draw": match.odds_draw,
                "odds_away": match.odds_away,
                "bookmaker": match.bookmaker,
                "confidence": match.confidence,
            })
        
        return pd.DataFrame(data)

    def fetch_all_live_matches(
        self,
        sports: List[str] = None,
        days_ahead: int = 7
    ) -> pd.DataFrame:
        """
        Fetch all live matches across multiple sports.
        
        Args:
            sports: List of sports to fetch (default: ["soccer", "basketball", "nfl"])
            days_ahead: Days to look ahead
            
        Returns:
            Combined DataFrame of all matches
        """
        if sports is None:
            sports = ["soccer", "basketball"]
        
        all_matches = []
        
        if "soccer" in sports:
            all_matches.extend(self.fetch_live_soccer_matches(days_ahead=days_ahead))
        
        if "basketball" in sports:
            all_matches.extend(self.fetch_live_basketball_matches(days_ahead=days_ahead))
        
        if "nfl" in sports:
            all_matches.extend(self.fetch_live_nfl_matches(days_ahead=days_ahead))
        
        return self.to_dataframe(all_matches)


# Singleton pattern for easy access
_live_fetcher = None


def get_live_fetcher() -> LiveSportsDataFetcher:
    """Get or create singleton instance of LiveSportsDataFetcher."""
    global _live_fetcher
    if _live_fetcher is None:
        _live_fetcher = LiveSportsDataFetcher()
    return _live_fetcher
