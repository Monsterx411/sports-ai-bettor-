#!/usr/bin/env python3
"""
Advanced Model Training with Feature Engineering
Trains model on 300-500+ match dataset with engineered features
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, confusion_matrix, roc_auc_score, roc_curve)
import matplotlib.pyplot as plt
import logging
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_pipeline import DataPipeline
from src.logger import setup_logger


def train_advanced_model(df: pd.DataFrame, model_name: str = 'advanced_model', 
                         test_size: float = 0.2, random_state: int = 42) -> dict:
    """
    Train advanced ensemble model with feature engineering
    
    Args:
        df: DataFrame with engineered features
        model_name: Name for saving the model
        test_size: Fraction of data for testing
        random_state: Random seed for reproducibility
    
    Returns:
        Dictionary with training metrics
    """
    
    logger.info("\n" + "="*70)
    logger.info("🤖 ADVANCED MODEL TRAINING")
    logger.info("="*70)
    
    # Prepare data
    target_col = 'home_win'
    
    if target_col not in df.columns:
        logger.error(f"Target column '{target_col}' not found in dataset")
        return {}
    
    # Select numeric features (exclude non-numeric and target)
    feature_cols = [col for col in df.columns 
                   if col != target_col 
                   and df[col].dtype in ['float64', 'int64', 'float32', 'int32']]
    
    # Remove any columns with all NaNs
    feature_cols = [col for col in feature_cols if df[col].notna().sum() > 0]
    
    logger.info(f"\n📊 Dataset Preparation:")
    logger.info(f"  Total records: {len(df)}")
    logger.info(f"  Features: {len(feature_cols)}")
    logger.info(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Fill missing values
    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df[target_col]
    
    logger.info(f"  Target distribution: {(y.value_counts().to_dict())}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    logger.info(f"\n📈 Train/Test Split:")
    logger.info(f"  Training set: {len(X_train)} samples")
    logger.info(f"  Test set: {len(X_test)} samples")
    logger.info(f"  Train target distribution: {dict(y_train.value_counts())}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train multiple models and ensemble them
    logger.info("\n🔨 Training ensemble models...")
    
    # Model 1: Random Forest (conservative)
    logger.info("  1. RandomForest (100 trees, max_depth=15)...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf.fit(X_train_scaled, y_train)
    
    # Model 2: Gradient Boosting
    logger.info("  2. GradientBoosting (150 estimators)...")
    gb = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=random_state,
        subsample=0.8
    )
    gb.fit(X_train_scaled, y_train)
    
    # Create ensemble
    logger.info("  3. Creating voting ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf),
            ('gb', gb),
        ],
        voting='soft'
    )
    ensemble.fit(X_train_scaled, y_train)
    
    # Evaluate models
    logger.info("\n📊 MODEL EVALUATION")
    logger.info("-" * 70)
    
    models = {
        'RandomForest': rf,
        'GradientBoosting': gb,
        'Ensemble': ensemble,
    }
    
    results = {}
    best_model = None
    best_accuracy = 0
    
    for model_name_local, model in models.items():
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
        
        results[model_name_local] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc,
            'model': model,
        }
        
        logger.info(f"\n{model_name_local}:")
        logger.info(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1 Score:  {f1:.4f}")
        logger.info(f"  AUC-ROC:   {auc:.4f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_model_name = model_name_local
    
    # Cross-validation
    logger.info(f"\n🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    logger.info(f"  CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
    logger.info(f"  Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Feature importance
    logger.info(f"\n⭐ TOP FEATURES ({best_model_name}):")
    
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']:.<35} {row['importance']:.4f}")
    
    # Save the best model
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / f'{best_model_name.lower()}.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': best_model,
            'scaler': scaler,
            'features': feature_cols,
            'feature_importance': feature_importance if hasattr(best_model, 'feature_importances_') else None,
        }, f)
    
    logger.info(f"\n✅ MODEL SAVED: {model_path}")
    logger.info(f"   Type: {best_model_name}")
    logger.info(f"   Accuracy: {best_accuracy*100:.2f}%")
    
    return {
        'model': best_model,
        'scaler': scaler,
        'features': feature_cols,
        'accuracy': best_accuracy,
        'model_name': best_model_name,
        'model_path': str(model_path),
        'all_results': results,
    }


def main():
    """Main execution"""
    
    # Check if combined dataset exists
    combined_path = Path('data/combined_training_data.csv')
    
    if not combined_path.exists():
        logger.info("Combined dataset not found. Running data pipeline...")
        pipeline = DataPipeline()
        df = pipeline.build_training_dataset(min_records=300)
    else:
        logger.info(f"Loading existing combined dataset: {combined_path}")
        df = pd.read_csv(combined_path)
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"Loaded {len(df)} records")
    
    # Train model
    results = train_advanced_model(df, model_name='advanced_model')
    
    if results:
        logger.info("\n" + "="*70)
        logger.info("✅ TRAINING COMPLETE!")
        logger.info("="*70)
        logger.info(f"\nBest Model: {results['model_name']}")
        logger.info(f"Accuracy: {results['accuracy']*100:.2f}%")
        logger.info(f"Features: {len(results['features'])}")
        logger.info(f"Saved to: {results['model_path']}")
        
        logger.info("\nNext steps:")
        logger.info("1. Make predictions: python cli_app.py predict --model-name advanced_model ...")
        logger.info("2. View dashboard: streamlit run web_app.py")
        logger.info("3. Analyze bets: python -c 'from src.predictor import *'")


if __name__ == '__main__':
    main()
