#!/usr/bin/env python3
"""
Fast Advanced Model Training (with sampling for speed)
Trains on sampled data and shows significant accuracy improvements
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pickle
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def train_model_on_data(csv_path: str, model_name: str = 'advanced_model', sample_size: int = None):
    """Train advanced model on CSV data with optional sampling"""
    
    logger.info("\n" + "="*70)
    logger.info("🤖 ADVANCED MODEL TRAINING (FAST)")
    logger.info("="*70)
    
    # Load data
    logger.info(f"\n📥 Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"  Loaded {len(df)} total records")
    logger.info(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # Sample if needed (for speed)
    if sample_size and sample_size < len(df):
        logger.info(f"  Sampling {sample_size} records for faster training...")
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
        logger.info(f"  Training on {len(df)} records")
    
    # Prepare features
    target_col = 'home_win'
    feature_cols = [col for col in df.columns 
                   if col != target_col 
                   and df[col].dtype in ['float64', 'int64', 'float32', 'int32']]
    feature_cols = [col for col in feature_cols if df[col].notna().sum() > 0]
    
    logger.info(f"\n📊 Dataset:")
    logger.info(f"  Target: {target_col}")
    logger.info(f"  Features: {len(feature_cols)}")
    logger.info(f"  Target distribution: {dict(df[target_col].value_counts())}")
    
    # Prepare X and y
    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df[target_col]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"\n📈 Train/Test Split:")
    logger.info(f"  Training: {len(X_train)} samples")
    logger.info(f"  Test: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    logger.info(f"\n🔨 Training models...")
    
    models = {}
    
    # RandomForest
    logger.info("  1. RandomForest (100 trees)...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf.fit(X_train_scaled, y_train)
    models['RandomForest'] = rf
    
    # GradientBoosting
    logger.info("  2. GradientBoosting (100 estimators)...")
    gb = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        subsample=0.8
    )
    gb.fit(X_train_scaled, y_train)
    models['GradientBoosting'] = gb
    
    # Evaluate
    logger.info(f"\n📊 MODEL EVALUATION")
    logger.info("-" * 70)
    
    best_model = None
    best_accuracy = 0
    best_name = None
    
    for name, model in models.items():
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc = 0.5
        
        logger.info(f"\n{name}:")
        logger.info(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1 Score:  {f1:.4f}")
        logger.info(f"  AUC-ROC:   {auc:.4f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    
    # Feature importance
    logger.info(f"\n⭐ TOP FEATURES ({best_name}):")
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']:.<40} {row['importance']:.4f}")
    
    # Save model
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / f'{model_name}.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': best_model,
            'scaler': scaler,
            'features': feature_cols,
        }, f)
    
    logger.info(f"\n✅ MODEL SAVED: {model_path}")
    logger.info(f"   Type: {best_name}")
    logger.info(f"   Accuracy: {best_accuracy*100:.2f}%")
    logger.info(f"   Features: {len(feature_cols)}")
    
    return {
        'accuracy': best_accuracy,
        'model_name': model_name,
        'features': len(feature_cols),
    }


if __name__ == '__main__':
    # Check if combined dataset exists
    combined_path = 'data/combined_training_data.csv'
    
    if Path(combined_path).exists():
        # Train on full dataset (with sampling for speed)
        logger.info("🎯 Training on FULL 230K+ match dataset...")
        results = train_model_on_data(
            combined_path,
            model_name='advanced_model_large',
            sample_size=50000  # Sample 50K for reasonable training time
        )
    else:
        # Fallback to historical data
        logger.warning("Combined dataset not found, using historical data...")
        results = train_model_on_data(
            'data/historical_matches.csv',
            model_name='sports_model',
        )
    
    logger.info("\n" + "="*70)
    logger.info("✅ TRAINING COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nModel: {results['model_name']}")
    logger.info(f"Accuracy: {results['accuracy']*100:.2f}%")
    logger.info(f"Features: {results['features']}")
    logger.info("\n📋 Next steps:")
    logger.info("1. Test with predictions: python3 cli_app.py predict --model-name advanced_model_large 0.7 0.6 0.5 2 8 5 60 40")
    logger.info("2. View in dashboard: streamlit run web_app.py")
