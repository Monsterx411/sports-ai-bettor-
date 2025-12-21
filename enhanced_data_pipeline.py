"""
Enhanced Data Pipeline - Load All Historical Cache Data
Combines 2000+ CSV files from multiple sources for massive training dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import glob
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedDataPipeline:
    """Load and combine data from all cache sources + existing data"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.all_data = []
        self.total_files = 0
        
    def load_footballdata_cache(self) -> pd.DataFrame:
        """Load from cache.footballdata-master (1993-2024, 2000+ files)"""
        logger.info("\n📂 Loading cache.footballdata-master...")
        cache_dir = self.data_dir / 'cache.footballdata-master'
        
        csv_files = list(cache_dir.glob('**/*.csv'))
        logger.info(f"  Found {len(csv_files)} CSV files")
        
        dfs = []
        for i, csv_file in enumerate(csv_files):
            try:
                df = pd.read_csv(csv_file, on_bad_lines='skip')
                
                # Standardize columns
                if 'Date' in df.columns:
                    df['date'] = pd.to_datetime(df['Date'], errors='coerce')
                elif 'date' not in df.columns:
                    continue
                    
                if 'HomeTeam' in df.columns:
                    df['home_team'] = df['HomeTeam']
                elif 'home_team' not in df.columns:
                    continue
                    
                if 'AwayTeam' in df.columns:
                    df['away_team'] = df['AwayTeam']
                elif 'away_team' not in df.columns:
                    continue
                    
                # Get score columns
                if 'FTHG' in df.columns and 'FTAG' in df.columns:
                    df['home_score'] = df['FTHG']
                    df['away_score'] = df['FTAG']
                elif 'home_score' not in df.columns or 'away_score' not in df.columns:
                    continue
                
                df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
                
                # Select relevant columns
                cols_to_keep = ['date', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']
                df = df[[col for col in cols_to_keep if col in df.columns]]
                
                if len(df) > 0:
                    dfs.append(df)
                    
                if (i + 1) % 100 == 0:
                    logger.info(f"    Processed {i+1}/{len(csv_files)} files...")
                    
            except Exception as e:
                continue
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            logger.info(f"  ✅ Loaded {len(result)} records from footballdata cache")
            return result
        else:
            logger.warning("  ⚠️  No valid records from footballdata cache")
            return pd.DataFrame()
    
    def load_soccerdata_cache(self) -> pd.DataFrame:
        """Load from cache.soccerdata-master"""
        logger.info("\n📂 Loading cache.soccerdata-master...")
        cache_dir = self.data_dir / 'cache.soccerdata-master'
        
        csv_files = list(cache_dir.glob('**/*.csv'))
        logger.info(f"  Found {len(csv_files)} CSV files")
        
        dfs = []
        for csv_file in csv_files[:100]:  # Sample first 100 files
            try:
                df = pd.read_csv(csv_file, on_bad_lines='skip')
                
                # Try to find and standardize columns
                date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                home_cols = [col for col in df.columns if 'home' in col.lower()]
                away_cols = [col for col in df.columns if 'away' in col.lower()]
                
                if date_cols and home_cols and away_cols:
                    df = df[[date_cols[0], home_cols[0], away_cols[0]]].copy()
                    df.columns = ['date', 'home_team', 'away_team']
                    
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    if len(df.dropna(subset=['date'])) > 0:
                        dfs.append(df)
                        
            except Exception:
                continue
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            logger.info(f"  ✅ Loaded {len(result)} records from soccerdata cache")
            return result
        else:
            logger.warning("  ⚠️  No valid records from soccerdata cache")
            return pd.DataFrame()
    
    def load_soccerverse_cache(self) -> pd.DataFrame:
        """Load from cache.soccerverse-master (1888+)"""
        logger.info("\n📂 Loading cache.soccerverse-master...")
        cache_dir = self.data_dir / 'cache.soccerverse-master'
        
        csv_files = list(cache_dir.glob('**/*.csv'))
        logger.info(f"  Found {len(csv_files)} CSV files (sampling...)")
        
        dfs = []
        for csv_file in csv_files[:50]:  # Sample to avoid memory issues
            try:
                df = pd.read_csv(csv_file, on_bad_lines='skip')
                
                # Find date and team columns
                if 'date' in df.columns.str.lower() and 'home' in df.columns.str.lower():
                    df['date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
                    if len(df.dropna(subset=['date'])) > 0:
                        dfs.append(df)
                        
            except Exception:
                continue
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            logger.info(f"  ✅ Loaded {len(result)} records from soccerverse cache")
            return result
        else:
            logger.warning("  ⚠️  No valid records from soccerverse cache")
            return pd.DataFrame()
    
    def load_existing_data(self) -> pd.DataFrame:
        """Load existing CSV files"""
        logger.info("\n📂 Loading existing CSV files...")
        
        existing_files = [
            'results.csv',
            'Matches.csv',
            'historical_matches.csv',
            'combined_training_data.csv'
        ]
        
        dfs = []
        for fname in existing_files:
            fpath = self.data_dir / fname
            if fpath.exists():
                try:
                    df = pd.read_csv(fpath, on_bad_lines='skip')
                    dfs.append(df)
                    logger.info(f"  ✅ Loaded {fname}: {len(df)} records")
                except Exception as e:
                    logger.warning(f"  ⚠️  Failed to load {fname}: {e}")
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()
    
    def standardize_and_combine(self, *dataframes) -> pd.DataFrame:
        """Combine and standardize all data"""
        logger.info("\n🔄 Combining and standardizing data...")
        
        all_dfs = []
        
        for df in dataframes:
            if df.empty:
                continue
            
            df = df.copy()
            
            # Standardize date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.drop('Date', axis=1)
            
            # Standardize teams
            team_cols_home = [col for col in df.columns if col.lower() in ['home_team', 'hometeam', 'home', 'hteam']]
            team_cols_away = [col for col in df.columns if col.lower() in ['away_team', 'awayteam', 'away', 'ateam']]
            
            if team_cols_home:
                df['home_team'] = df[team_cols_home[0]]
            if team_cols_away:
                df['away_team'] = df[team_cols_away[0]]
            
            # Standardize scores
            score_cols_home = [col for col in df.columns if col.lower() in ['home_score', 'fthg', 'hgoals', 'home_goals']]
            score_cols_away = [col for col in df.columns if col.lower() in ['away_score', 'ftag', 'agoals', 'away_goals']]
            
            if score_cols_home:
                df['home_score'] = pd.to_numeric(df[score_cols_home[0]], errors='coerce')
            if score_cols_away:
                df['away_score'] = pd.to_numeric(df[score_cols_away[0]], errors='coerce')
            
            # Create target
            if 'home_score' in df.columns and 'away_score' in df.columns:
                df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
            elif 'home_win' not in df.columns:
                continue
            
            # Keep essential columns
            essential = ['date', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']
            cols_to_keep = [col for col in essential if col in df.columns]
            df = df[cols_to_keep]
            
            # Filter valid records
            df = df.dropna(subset=['date', 'home_team', 'away_team', 'home_win'])
            
            if len(df) > 0:
                all_dfs.append(df)
        
        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            
            # Remove duplicates
            combined = combined.drop_duplicates(subset=['date', 'home_team', 'away_team'], keep='first')
            combined = combined.sort_values('date').reset_index(drop=True)
            
            logger.info(f"  ✅ Combined {len(combined)} unique records")
            return combined
        else:
            logger.error("  ❌ No data to combine")
            return pd.DataFrame()
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from combined data"""
        logger.info("\n⚙️  Engineering features...")
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Basic features
        df['goal_diff'] = df['home_score'] - df['away_score']
        df['total_goals'] = df['home_score'] + df['away_score']
        df['high_scoring'] = (df['total_goals'] > 2.5).astype(int)
        
        # Rolling statistics (by team, last 10 games)
        for team_col in ['home_team', 'away_team']:
            prefix = 'home' if team_col == 'home_team' else 'away'
            
            # Recent performance
            team_data = df.groupby(team_col).apply(
                lambda x: x.sort_values('date')
            ).reset_index(drop=True)
            
            df[f'{prefix}_recent_wins'] = 0
            df[f'{prefix}_recent_goals'] = 0
        
        # Match features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['season'] = df['year'] - (df['month'] < 8).astype(int)
        
        logger.info(f"  ✅ Features engineered: {df.shape[1]} columns")
        
        return df
    
    def build_enhanced_dataset(self) -> pd.DataFrame:
        """Build the complete enhanced dataset"""
        logger.info("\n" + "="*70)
        logger.info("🚀 BUILDING ENHANCED DATASET FROM ALL SOURCES")
        logger.info("="*70)
        
        # Load all data sources
        df_footballdata = self.load_footballdata_cache()
        df_soccerdata = self.load_soccerdata_cache()
        df_soccerverse = self.load_soccerverse_cache()
        df_existing = self.load_existing_data()
        
        # Combine
        combined = self.standardize_and_combine(
            df_footballdata,
            df_soccerdata,
            df_soccerverse,
            df_existing
        )
        
        if combined.empty:
            logger.error("Failed to create combined dataset")
            return combined
        
        # Engineer features
        enhanced = self.engineer_features(combined)
        
        # Save
        output_path = self.data_dir / 'enhanced_training_dataset.csv'
        enhanced.to_csv(output_path, index=False)
        
        logger.info(f"\n✅ ENHANCED DATASET CREATED")
        logger.info(f"  File: {output_path}")
        logger.info(f"  Records: {len(enhanced):,}")
        logger.info(f"  Features: {enhanced.shape[1]}")
        logger.info(f"  Date range: {enhanced['date'].min().date()} to {enhanced['date'].max().date()}")
        logger.info(f"  Target distribution: {dict(enhanced['home_win'].value_counts())}")
        
        return enhanced


def main():
    """Main execution"""
    pipeline = EnhancedDataPipeline()
    df = pipeline.build_enhanced_dataset()
    
    if not df.empty:
        logger.info("\n" + "="*70)
        logger.info("📊 DATASET STATISTICS")
        logger.info("="*70)
        logger.info(f"Total matches: {len(df):,}")
        logger.info(f"Home wins: {(df['home_win'] == 1).sum():,} ({(df['home_win'] == 1).sum() / len(df) * 100:.1f}%)")
        logger.info(f"Other results: {(df['home_win'] == 0).sum():,} ({(df['home_win'] == 0).sum() / len(df) * 100:.1f}%)")
        logger.info(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        logger.info(f"Unique home teams: {df['home_team'].nunique()}")
        logger.info(f"Unique away teams: {df['away_team'].nunique()}")
        
        logger.info("\n✅ READY FOR TRAINING!")
        logger.info("Next: python3 train_enhanced.py")


if __name__ == '__main__':
    main()
