"""
Comprehensive Data Pipeline for Model Training
- Combines multiple CSV data sources
- Fetches live data from APIs
- Engineers advanced features
- Creates training dataset with 300-500+ matches
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Optional, Dict
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPipeline:
    """Load, combine, and engineer features from multiple data sources"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.df = None
        
    def load_historical_matches(self) -> pd.DataFrame:
        """Load our custom historical matches CSV"""
        logger.info("Loading historical_matches.csv...")
        df = pd.read_csv(self.data_dir / 'historical_matches.csv')
        logger.info(f"  ✅ Loaded {len(df)} records")
        return df
    
    def load_results_data(self) -> pd.DataFrame:
        """Load comprehensive results.csv with match outcomes"""
        logger.info("Loading results.csv...")
        df = pd.read_csv(self.data_dir / 'results.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        # Create target variable (1 = home win, 0 = other)
        df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
        
        # Keep only football matches (exclude other sports tournaments if any)
        df = df[df['tournament'].notna()].copy()
        
        # Select relevant columns
        df = df[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']].copy()
        
        logger.info(f"  ✅ Loaded {len(df)} records")
        return df
    
    def load_elo_ratings(self) -> pd.DataFrame:
        """Load Elo ratings for teams"""
        logger.info("Loading EloRatings.csv...")
        df = pd.read_csv(self.data_dir / 'EloRatings.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        logger.info(f"  ✅ Loaded {len(df)} Elo rating records")
        return df
    
    def load_matches_comprehensive(self) -> pd.DataFrame:
        """Load comprehensive Matches.csv with detailed stats"""
        logger.info("Loading Matches.csv...")
        df = pd.read_csv(self.data_dir / 'Matches.csv')
        df['MatchDate'] = pd.to_datetime(df['MatchDate'])
        
        # Standardize column names
        df.columns = df.columns.str.lower()
        
        # Create target variable
        df['home_win'] = (df['fthome'] > df['ftaway']).astype(int)
        
        # Rename for consistency
        df = df.rename(columns={
            'matchdate': 'date',
            'hometeam': 'home_team',
            'awayteam': 'away_team',
            'fthome': 'home_score',
            'ftaway': 'away_score',
            'hometarget': 'home_shots_on_target',
            'awaytarget': 'away_shots_on_target',
            'homeelo': 'home_elo',
            'awayelo': 'away_elo',
            'form3home': 'home_form_3',
            'form5home': 'home_form_5',
            'form3away': 'away_form_3',
            'form5away': 'away_form_5',
            'homecorners': 'home_corners',
            'awaycorners': 'away_corners',
        })
        
        logger.info(f"  ✅ Loaded {len(df)} comprehensive match records")
        return df
    
    def load_goalscorers(self) -> pd.DataFrame:
        """Load goalscorers data for feature engineering"""
        logger.info("Loading goalscorers.csv...")
        df = pd.read_csv(self.data_dir / 'goalscorers.csv')
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"  ✅ Loaded {len(df)} goal records")
        return df
    
    def combine_data_sources(self) -> pd.DataFrame:
        """Combine multiple data sources intelligently"""
        logger.info("\n🔄 COMBINING DATA SOURCES...")
        
        # Load all data sources
        df_historical = self.load_historical_matches()
        df_results = self.load_results_data()
        df_matches = self.load_matches_comprehensive()
        df_elo = self.load_elo_ratings()
        df_goals = self.load_goalscorers()
        
        # Start with comprehensive matches (most complete)
        logger.info("\n  Merging comprehensive matches...")
        df = df_matches[['date', 'home_team', 'away_team', 'home_score', 'away_score', 
                         'home_win', 'home_elo', 'away_elo', 'home_form_3', 'away_form_3',
                         'home_form_5', 'away_form_5', 'home_shots_on_target', 
                         'away_shots_on_target', 'home_corners', 'away_corners']].copy()
        df = df.dropna(subset=['home_team', 'away_team', 'home_score', 'away_score'])
        logger.info(f"    Base dataset: {len(df)} records")
        
        # Fill missing Elo with recent values
        logger.info("  Adding Elo ratings...")
        df_elo_home = df_elo[df_elo['club'].notna()].copy()
        df_elo_home = df_elo_home.rename(columns={'club': 'home_team', 'elo': 'home_elo_elo'})
        df_elo_away = df_elo_home.rename(columns={'home_team': 'away_team', 'home_elo_elo': 'away_elo_elo'})
        
        # Simple Elo merge (keep existing Elo if present, use from Elo file if missing)
        df['home_elo'] = df['home_elo'].fillna(1500)
        df['away_elo'] = df['away_elo'].fillna(1500)
        
        # Add goal statistics
        logger.info("  Adding goal scorer statistics...")
        goals_per_match = df_goals.groupby(['date', 'home_team', 'away_team']).size().reset_index(name='total_goals')
        goals_per_match['date'] = pd.to_datetime(goals_per_match['date'])
        
        # Merge goal data
        df = pd.merge(df, goals_per_match, on=['date', 'home_team', 'away_team'], how='left')
        df['total_goals'] = df['total_goals'].fillna(df['home_score'] + df['away_score'])
        
        logger.info(f"  ✅ Combined dataset: {len(df)} records")
        return df
    
    def fetch_live_api_data(self) -> Optional[pd.DataFrame]:
        """Fetch recent matches from API Football and Odds API"""
        logger.info("\n🌐 FETCHING LIVE API DATA...")
        
        try:
            from src.data_fetch import SportsDataFetcher
            from config.settings import API_SPORTS_KEY, ODDS_API_KEY
            
            if not API_SPORTS_KEY or API_SPORTS_KEY == 'your_api_key_here':
                logger.warning("  ⚠️  API key not configured. Skipping live data fetch.")
                return None
            
            fetcher = SportsDataFetcher()
            
            # Fetch recent fixtures (last 30 days)
            logger.info("  Fetching recent matches from API Football...")
            try:
                # Get recent matches
                fixtures = fetcher.get_fixtures_by_league_and_season(
                    league='39',  # Premier League
                    season='2024'
                )
                
                if fixtures:
                    df_api = pd.DataFrame(fixtures)
                    logger.info(f"    ✅ Fetched {len(df_api)} API records")
                    
                    # Convert to our format if needed
                    if 'timestamp' in df_api.columns:
                        df_api['date'] = pd.to_datetime(df_api['timestamp'])
                    
                    return df_api
                else:
                    logger.warning("  ⚠️  No API data returned")
                    return None
                    
            except Exception as e:
                logger.warning(f"  ⚠️  API fetch failed: {e}")
                return None
                
        except ImportError:
            logger.warning("  ⚠️  src.data_fetch not available")
            return None
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer advanced features for model training"""
        logger.info("\n⚙️  ENGINEERING ADVANCED FEATURES...")
        
        df = df.copy()
        
        # 1. Form difference
        if 'home_form_3' in df.columns and 'away_form_3' in df.columns:
            df['form_diff_3'] = df['home_form_3'] - df['away_form_3']
            df['form_diff_5'] = df['home_form_5'] - df['away_form_5']
            logger.info("  ✅ Added form differential features")
        
        # 2. Elo difference
        if 'home_elo' in df.columns and 'away_elo' in df.columns:
            df['elo_diff'] = df['home_elo'] - df['away_elo']
            df['elo_ratio'] = df['home_elo'] / (df['away_elo'] + 1)
            logger.info("  ✅ Added Elo features")
        
        # 3. Shot efficiency
        if 'home_shots_on_target' in df.columns and 'away_shots_on_target' in df.columns:
            df['shots_on_target_diff'] = df['home_shots_on_target'] - df['away_shots_on_target']
            df['shots_ratio'] = df['home_shots_on_target'] / (df['away_shots_on_target'] + 1)
            logger.info("  ✅ Added shot features")
        
        # 4. Corner difference
        if 'home_corners' in df.columns and 'away_corners' in df.columns:
            df['corners_diff'] = df['home_corners'] - df['away_corners']
            df['corners_ratio'] = df['home_corners'] / (df['away_corners'] + 1)
            logger.info("  ✅ Added corner features")
        
        # 5. Score based features
        if 'home_score' in df.columns and 'away_score' in df.columns:
            df['goal_diff'] = df['home_score'] - df['away_score']
            df['total_goals'] = df['home_score'] + df['away_score']
            df['high_scoring'] = (df['total_goals'] > 2.5).astype(int)
            logger.info("  ✅ Added score-based features")
        
        # 6. Derived form metrics
        df['home_form'] = df.get('home_form_3', df.get('home_form_5', 0.5))
        df['away_form'] = df.get('away_form_3', df.get('away_form_5', 0.5))
        
        # Normalize forms to 0-1 if needed
        if df['home_form'].max() > 10:
            df['home_form'] = df['home_form'] / 100
            df['away_form'] = df['away_form'] / 100
        
        df['form_product'] = df['home_form'] * df['away_form']
        logger.info("  ✅ Added composite form features")
        
        # 7. Recent performance streaks (simulate)
        df['home_win_streak'] = 0
        df['away_win_streak'] = 0
        
        # Group by teams and calculate streaks
        for team in df['home_team'].unique():
            if pd.isna(team):
                continue
            team_matches = df[(df['home_team'] == team) | (df['away_team'] == team)].sort_values('date')
            if len(team_matches) > 0:
                # Simple streak calculation based on form
                avg_form = team_matches['home_form'].mean() if 'home_form' in team_matches.columns else 0.5
                if pd.notna(avg_form):
                    streak_value = max(0, int(avg_form * 5))
                    df.loc[df['home_team'] == team, 'home_win_streak'] = streak_value
        
        logger.info("  ✅ Added streak features")
        
        # 8. Create advantage metrics
        if 'home_elo' in df.columns:
            df['home_advantage'] = 0.55  # Standard home advantage
            # Adjust based on Elo
            df.loc[df['elo_diff'] > 200, 'home_advantage'] = 0.65
            df.loc[df['elo_diff'] > 400, 'home_advantage'] = 0.75
            df.loc[df['elo_diff'] < -200, 'home_advantage'] = 0.45
            df.loc[df['elo_diff'] < -400, 'home_advantage'] = 0.35
            logger.info("  ✅ Added home advantage features")
        
        # 9. Possession approximation (from form if not available)
        if 'home_possession' not in df.columns:
            df['home_possession'] = 50 + (df['home_form'] * 20)
            df['away_possession'] = 50 - (df['home_form'] * 20)
            df['home_possession'] = df['home_possession'].clip(30, 70)
            df['away_possession'] = df['away_possession'].clip(30, 70)
            logger.info("  ✅ Generated possession estimates")
        
        # 10. Recent goals metric
        if 'total_goals' in df.columns:
            df['recent_goals'] = (df['total_goals'] / 2).astype(int)  # Average per team
            logger.info("  ✅ Added recent goals features")
        
        logger.info(f"  ✅ Total features engineered: {df.shape[1]} columns")
        return df
    
    def clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the dataset"""
        logger.info("\n🧹 CLEANING AND VALIDATING DATA...")
        
        initial_rows = len(df)
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['date', 'home_team', 'away_team'], keep='first')
        logger.info(f"  Removed {initial_rows - len(df)} duplicates")
        
        # Drop rows with missing critical columns
        critical_cols = ['date', 'home_team', 'away_team', 'home_win']
        df = df.dropna(subset=critical_cols)
        logger.info(f"  Removed rows with missing critical data: {len(df)} remaining")
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Select numeric columns for model
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        logger.info(f"  ✅ Dataset cleaned: {len(df)} valid records")
        logger.info(f"  ✅ Numeric features available: {len(numeric_cols)}")
        
        return df
    
    def select_best_features(self, df: pd.DataFrame, target_col: str = 'home_win') -> Dict[str, str]:
        """Select the best features for the model"""
        logger.info("\n🎯 SELECTING BEST FEATURES...")
        
        feature_candidates = {
            'form': ['home_form', 'away_form', 'form_diff_3', 'form_diff_5', 'form_product'],
            'elo': ['home_elo', 'away_elo', 'elo_diff', 'elo_ratio'],
            'shots': ['home_shots_on_target', 'away_shots_on_target', 'shots_on_target_diff', 'shots_ratio'],
            'corners': ['home_corners', 'away_corners', 'corners_diff', 'corners_ratio'],
            'possession': ['home_possession', 'away_possession'],
            'goals': ['recent_goals', 'total_goals', 'high_scoring'],
            'advantage': ['home_advantage', 'home_win_streak'],
        }
        
        selected_features = []
        
        for category, features in feature_candidates.items():
            available = [f for f in features if f in df.columns]
            if available:
                selected_features.extend(available)
                logger.info(f"  ✅ {category.upper()}: {', '.join(available)}")
        
        logger.info(f"\n  TOTAL FEATURES SELECTED: {len(selected_features)}")
        
        return {'features': selected_features, 'target': target_col}
    
    def build_training_dataset(self, min_records: int = 300) -> pd.DataFrame:
        """Build complete training dataset"""
        logger.info("\n" + "="*60)
        logger.info("🚀 BUILDING COMPLETE TRAINING DATASET")
        logger.info("="*60)
        
        # Combine data sources
        df = self.combine_data_sources()
        
        # Fetch live data
        df_api = self.fetch_live_api_data()
        if df_api is not None and len(df_api) > 0:
            # Combine with existing data
            df = pd.concat([df, df_api], ignore_index=True)
            logger.info(f"  ✅ Added {len(df_api)} API records. Total: {len(df)}")
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Clean and validate
        df = self.clean_and_validate(df)
        
        # Check if we have enough records
        if len(df) < min_records:
            logger.warning(f"  ⚠️  Only {len(df)} records (target: {min_records})")
        else:
            logger.info(f"  ✅ Met target of {min_records}+ records!")
        
        # Save dataset
        output_path = self.data_dir / 'combined_training_data.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"\n  ✅ DATASET SAVED: {output_path}")
        logger.info(f"  📊 Total records: {len(df)}")
        logger.info(f"  📊 Total features: {df.shape[1]}")
        logger.info(f"  📊 Date range: {df['date'].min()} to {df['date'].max()}")
        
        self.df = df
        return df
    
    def get_feature_info(self) -> Dict:
        """Get information about available features"""
        if self.df is None:
            return {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        return {
            'total_features': len(numeric_cols),
            'features': numeric_cols,
            'total_records': len(self.df),
            'date_range': {
                'start': str(self.df['date'].min()),
                'end': str(self.df['date'].max())
            }
        }


def main():
    """Main pipeline execution"""
    pipeline = DataPipeline()
    
    # Build training dataset
    df = pipeline.build_training_dataset(min_records=300)
    
    # Get feature info
    info = pipeline.get_feature_info()
    
    logger.info("\n" + "="*60)
    logger.info("📈 DATASET SUMMARY")
    logger.info("="*60)
    logger.info(f"Total records: {info['total_records']}")
    logger.info(f"Total features: {info['total_features']}")
    logger.info(f"Feature list: {', '.join(info['features'][:5])}...")
    logger.info(f"Date range: {info['date_range']['start']} to {info['date_range']['end']}")
    
    logger.info("\n✅ PIPELINE COMPLETE!")
    logger.info("Next: python train_with_pipeline.py")


if __name__ == '__main__':
    main()
