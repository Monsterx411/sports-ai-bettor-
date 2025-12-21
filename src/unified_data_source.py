"""
Unified Data Source Manager
Seamlessly combines historical CSV data with live API data for training and predictions.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import logging

from src.live_sports_data import get_live_fetcher, LiveMatch
from src.data_fetch import SportsDataFetcher
from config.settings import settings

logger = logging.getLogger(__name__)


class UnifiedDataSourceManager:
    """
    Manages both historical and live data sources.
    Provides unified interface for model training and predictions.
    """

    def __init__(self):
        """Initialize manager with both data sources."""
        self.live_fetcher = get_live_fetcher()
        self.api_fetcher = SportsDataFetcher()
        self.cache = {}

    def get_training_data(
        self,
        source: str = "historical",
        sport: str = "soccer",
        min_samples: int = 100,
        date_range: Optional[Tuple[str, str]] = None
    ) -> pd.DataFrame:
        """
        Get training data from specified source.
        
        Args:
            source: "historical", "live", or "combined"
            sport: Sport type
            min_samples: Minimum samples required
            date_range: (start_date, end_date) as YYYY-MM-DD strings
            
        Returns:
            DataFrame ready for training
        """
        if source == "historical":
            return self._get_historical_data(sport, date_range)
        elif source == "live":
            return self._get_live_data(sport)
        elif source == "combined":
            return self._combine_data_sources(sport, date_range)
        else:
            raise ValueError(f"Unknown source: {source}")

    def _get_historical_data(
        self,
        sport: str,
        date_range: Optional[Tuple[str, str]] = None
    ) -> pd.DataFrame:
        """Get historical CSV data with optional filtering."""
        cache_key = f"historical_{sport}_{date_range}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        logger.info(f"Loading historical {sport} data...")
        
        # Load from data directory
        data_dir = Path(settings.DATA_DIR)
        csv_files = list(data_dir.glob("*.csv"))
        
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Standardize columns if needed
                df = self._standardize_columns(df, sport)
                if df is not None and len(df) > 0:
                    dfs.append(df)
            except Exception as e:
                logger.warning(f"Error loading {csv_file}: {e}")
        
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            
            # Apply date range filter if provided
            if date_range:
                df = self._filter_by_date_range(df, date_range)
            
            # Cache result
            self.cache[cache_key] = df
            logger.info(f"Loaded {len(df)} historical records")
            return df
        
        return pd.DataFrame()

    def _get_live_data(self, sport: str) -> pd.DataFrame:
        """Get live data from APIs."""
        cache_key = f"live_{sport}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        logger.info(f"Fetching live {sport} data...")
        
        try:
            df = self.live_fetcher.fetch_all_live_matches(
                sports=[sport],
                days_ahead=7
            )
            
            if len(df) > 0:
                # Cache result
                self.cache[cache_key] = df
                logger.info(f"Fetched {len(df)} live matches")
            
            return df
        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            return pd.DataFrame()

    def _combine_data_sources(
        self,
        sport: str,
        date_range: Optional[Tuple[str, str]] = None
    ) -> pd.DataFrame:
        """Combine historical and live data."""
        cache_key = f"combined_{sport}_{date_range}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        logger.info(f"Combining historical and live {sport} data...")
        
        historical_df = self._get_historical_data(sport, date_range)
        live_df = self._get_live_data(sport)
        
        # Combine
        combined = []
        if len(historical_df) > 0:
            combined.append(historical_df)
        if len(live_df) > 0:
            combined.append(live_df)
        
        if combined:
            df = pd.concat(combined, ignore_index=True)
            df = df.drop_duplicates(subset=["match_id"] if "match_id" in df.columns else None)
            
            # Cache result
            self.cache[cache_key] = df
            logger.info(f"Combined {len(df)} total records")
            return df
        
        return pd.DataFrame()

    @staticmethod
    def _standardize_columns(df: pd.DataFrame, sport: str) -> Optional[pd.DataFrame]:
        """Standardize column names for consistency."""
        try:
            # Common date columns
            date_cols = [col for col in df.columns if col.lower() in ['date', 'datetime', 'match_date', 'kickoff']]
            if date_cols:
                df['match_time'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
            # Team columns
            home_cols = [col for col in df.columns if 'home' in col.lower() and 'team' in col.lower()]
            away_cols = [col for col in df.columns if 'away' in col.lower() and 'team' in col.lower()]
            
            if home_cols:
                df['home_team'] = df[home_cols[0]]
            if away_cols:
                df['away_team'] = df[away_cols[0]]
            
            # Score columns
            home_score_cols = [col for col in df.columns if 'home' in col.lower() and 'score' in col.lower()]
            away_score_cols = [col for col in df.columns if 'away' in col.lower() and 'score' in col.lower()]
            
            if home_score_cols:
                df['home_score'] = pd.to_numeric(df[home_score_cols[0]], errors='coerce')
            if away_score_cols:
                df['away_score'] = pd.to_numeric(df[away_score_cols[0]], errors='coerce')
            
            # Odds columns
            odds_cols = [col for col in df.columns if 'odds' in col.lower() or 'price' in col.lower()]
            for col in odds_cols[:3]:
                if 'home' in col.lower() or '1' in col:
                    df['odds_home'] = pd.to_numeric(df[col], errors='coerce')
                elif 'draw' in col.lower() or 'x' in col.lower():
                    df['odds_draw'] = pd.to_numeric(df[col], errors='coerce')
                elif 'away' in col.lower() or '2' in col:
                    df['odds_away'] = pd.to_numeric(df[col], errors='coerce')
            
            # Keep only standardized columns
            standard_cols = [
                'match_time', 'home_team', 'away_team', 'home_score', 'away_score',
                'odds_home', 'odds_draw', 'odds_away', 'sport', 'league', 'status'
            ]
            available_cols = [col for col in standard_cols if col in df.columns]
            
            return df[available_cols] if available_cols else None
        
        except Exception as e:
            logger.warning(f"Error standardizing columns: {e}")
            return None

    @staticmethod
    def _filter_by_date_range(
        df: pd.DataFrame,
        date_range: Tuple[str, str]
    ) -> pd.DataFrame:
        """Filter DataFrame by date range."""
        try:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            
            if 'match_time' in df.columns:
                df['match_time'] = pd.to_datetime(df['match_time'], errors='coerce')
                return df[(df['match_time'] >= start_date) & (df['match_time'] <= end_date)]
            
            return df
        except Exception as e:
            logger.warning(f"Error filtering by date range: {e}")
            return df

    def get_live_odds(
        self,
        home_team: str,
        away_team: str,
        sport: str = "soccer"
    ) -> Dict[str, float]:
        """Get current live odds for a specific match."""
        live_data = self._get_live_data(sport)
        
        if live_data is not None and len(live_data) > 0:
            match = live_data[
                (live_data['home_team'].str.lower() == home_team.lower()) &
                (live_data['away_team'].str.lower() == away_team.lower())
            ]
            
            if len(match) > 0:
                row = match.iloc[0]
                return {
                    "home": row.get('odds_home'),
                    "draw": row.get('odds_draw'),
                    "away": row.get('odds_away'),
                    "bookmaker": row.get('bookmaker')
                }
        
        return {}

    def get_match_features(
        self,
        home_team: str,
        away_team: str,
        sport: str = "soccer",
        lookback_days: int = 365
    ) -> Optional[Dict[str, float]]:
        """
        Extract features for a specific match from historical data.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            lookback_days: Days to look back for statistics
            
        Returns:
            Dictionary of extracted features for ML model
        """
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        historical_df = self._get_historical_data(
            sport,
            date_range=(start_date, end_date)
        )
        
        if len(historical_df) == 0:
            return None
        
        # Calculate stats for home team
        home_stats = self._calculate_team_stats(
            historical_df,
            home_team,
            is_home=True
        )
        
        # Calculate stats for away team
        away_stats = self._calculate_team_stats(
            historical_df,
            away_team,
            is_home=False
        )
        
        # Combine features
        features = {
            "home_wins": home_stats.get("wins", 0),
            "home_draws": home_stats.get("draws", 0),
            "home_losses": home_stats.get("losses", 0),
            "home_goals_for": home_stats.get("goals_for", 0),
            "home_goals_against": home_stats.get("goals_against", 0),
            "away_wins": away_stats.get("wins", 0),
            "away_draws": away_stats.get("draws", 0),
            "away_losses": away_stats.get("losses", 0),
            "away_goals_for": away_stats.get("goals_for", 0),
            "away_goals_against": away_stats.get("goals_against", 0),
        }
        
        return features

    @staticmethod
    def _calculate_team_stats(
        df: pd.DataFrame,
        team_name: str,
        is_home: bool
    ) -> Dict[str, float]:
        """Calculate team statistics from matches."""
        if is_home:
            team_matches = df[df['home_team'].str.lower() == team_name.lower()].copy()
            team_matches['goals_for'] = team_matches['home_score']
            team_matches['goals_against'] = team_matches['away_score']
        else:
            team_matches = df[df['away_team'].str.lower() == team_name.lower()].copy()
            team_matches['goals_for'] = team_matches['away_score']
            team_matches['goals_against'] = team_matches['home_score']
        
        if len(team_matches) == 0:
            return {
                "wins": 0, "draws": 0, "losses": 0,
                "goals_for": 0, "goals_against": 0
            }
        
        # Calculate results
        team_matches['result'] = team_matches.apply(
            lambda x: 'W' if x['goals_for'] > x['goals_against']
            else 'D' if x['goals_for'] == x['goals_against']
            else 'L',
            axis=1
        )
        
        return {
            "wins": (team_matches['result'] == 'W').sum(),
            "draws": (team_matches['result'] == 'D').sum(),
            "losses": (team_matches['result'] == 'L').sum(),
            "goals_for": team_matches['goals_for'].sum(),
            "goals_against": team_matches['goals_against'].sum(),
            "avg_goals_for": team_matches['goals_for'].mean(),
            "avg_goals_against": team_matches['goals_against'].mean(),
        }

    def clear_cache(self) -> None:
        """Clear internal cache."""
        self.cache.clear()
        logger.info("Data cache cleared")


# Singleton pattern for easy access
_unified_manager = None


def get_unified_data_manager() -> UnifiedDataSourceManager:
    """Get or create singleton instance."""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = UnifiedDataSourceManager()
    return _unified_manager
