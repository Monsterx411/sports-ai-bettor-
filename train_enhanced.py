#!/usr/bin/env python3
"""
Enhanced Model Training with Massive Dataset
Trains on 500K+ match records from all sources combined
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pickle
import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


def train_enhanced_model(csv_path: str, sample_size: int = None, model_name: str = 'enhanced_model'):
    """Train on enhanced dataset"""
    
    logger.info("\n" + "="*70)
    logger.info("🤖 ENHANCED MODEL TRAINING (Multiple Data Sources)")
    logger.info("="*70)
    
    # Load data
    logger.info(f"\n📥 Loading {csv_path}...")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"  ✅ Loaded {len(df):,} total records")
    logger.info(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # Sample if specified
    if sample_size and sample_size < len(df):
        logger.info(f"  Sampling {sample_size:,} records for training...")
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    
    # Prepare features
    target_col = 'home_win'
    
    # Select numeric features
    feature_cols = [col for col in df.columns 
                   if col != target_col 
                   and df[col].dtype in ['float64', 'int64', 'float32', 'int32']]
    feature_cols = [col for col in feature_cols if df[col].notna().sum() > 0]
    
    logger.info(f"\n📊 Dataset:")
    logger.info(f"  Records: {len(df):,}")
    logger.info(f"  Features: {len(feature_cols)}")
    logger.info(f"  Target distribution: {dict(df[target_col].value_counts())}")
    
    # Prepare data
    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df[target_col]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"\n📈 Train/Test Split:")
    logger.info(f"  Training: {len(X_train):,} samples")
    logger.info(f"  Test: {len(X_test):,} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    logger.info(f"\n🔨 Training ensemble models...")
    
    models = {}
    
    # RandomForest
    logger.info("  1. RandomForest (200 trees, balanced)...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
        verbose=0
    )
    rf.fit(X_train_scaled, y_train)
    models['RandomForest'] = rf
    
    # GradientBoosting
    logger.info("  2. GradientBoosting (200 estimators)...")
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        subsample=0.8,
        verbose=0
    )
    gb.fit(X_train_scaled, y_train)
    models['GradientBoosting'] = gb
    
    # Voting Classifier
    logger.info("  3. Creating voting ensemble...")
    voting = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb)],
        voting='soft'
    )
    voting.fit(X_train_scaled, y_train)
    models['VotingEnsemble'] = voting
    
    # Evaluate
    logger.info(f"\n📊 MODEL EVALUATION")
    logger.info("-" * 70)
    
    best_model = None
    best_accuracy = 0
    best_name = None
    results_dict = {}
    
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
        
        results_dict[name] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc
        }
        
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
        importances = best_model.feature_importances_
        feature_imp = pd.DataFrame({
            'feature': feature_cols,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_imp.head(15).iterrows():
            logger.info(f"  {row['feature']:.<40} {row['importance']:.4f}")
    
    # Cross-validation
    logger.info(f"\n🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    logger.info(f"  Scores: {[f'{s:.4f}' for s in cv_scores]}")
    logger.info(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Save model
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / f'{model_name}.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': best_model,
            'scaler': scaler,
            'features': feature_cols,
            'model_name': best_name,
            'accuracy': best_accuracy,
            'cv_scores': cv_scores,
        }, f)
    
    logger.info(f"\n✅ MODEL SAVED: {model_path}")
    logger.info(f"   Type: {best_name}")
    logger.info(f"   Accuracy: {best_accuracy*100:.2f}%")
    logger.info(f"   Features: {len(feature_cols)}")
    logger.info(f"   CV Score: {cv_scores.mean():.4f}")
    
    return {
        'accuracy': best_accuracy,
        'model_name': best_name,
        'features': len(feature_cols),
        'model_path': str(model_path),
        'cv_mean': cv_scores.mean(),
    }


def main():
    """Main execution"""
    
    # Check for enhanced dataset
    enhanced_path = 'data/enhanced_training_dataset.csv'
    
    if not Path(enhanced_path).exists():
        logger.info("Enhanced dataset not found. Building from cache sources...")
        from enhanced_data_pipeline import EnhancedDataPipeline
        pipeline = EnhancedDataPipeline()
        df = pipeline.build_enhanced_dataset()
    
    # Train model
    if Path(enhanced_path).exists():
        logger.info(f"Training on enhanced dataset with ALL cache sources combined...")
        results = train_enhanced_model(
            enhanced_path,
            sample_size=None,  # Use all data
            model_name='enhanced_model_full'
        )
    else:
        logger.error("Could not load enhanced dataset")
        return
    
    if results:
        logger.info("\n" + "="*70)
        logger.info("✅ ENHANCED TRAINING COMPLETE!")
        logger.info("="*70)
        logger.info(f"\nBest Model: {results['model_name']}")
        logger.info(f"Accuracy: {results['accuracy']*100:.2f}%")
        logger.info(f"CV Score: {results['cv_mean']:.4f}")
        logger.info(f"Features: {results['features']}")
        logger.info(f"Saved to: {results['model_path']}")
        
        logger.info("\nNext steps:")
        logger.info("1. Make predictions: python3 cli_app.py predict --model-name enhanced_model_full 0.7 0.6 0.5 2 8 5 62 38")
        logger.info("2. View dashboard: streamlit run web_app.py")


if __name__ == '__main__':
    main()
