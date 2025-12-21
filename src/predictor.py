"""
ML prediction module for sports betting.
Handles model training, predictions, and value bet identification.
"""

from typing import Dict, List, Tuple, Optional, Any
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from datetime import datetime

from config.settings import settings, MODELS_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)


class ModelManager:
    """Manage ML models for predictions."""

    def __init__(self):
        """Initialize model manager."""
        self.model: Optional[RandomForestClassifier] = None
        self.feature_names: Optional[List[str]] = None
        self.model_metadata: Dict[str, Any] = {}

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "home_win",
        feature_cols: Optional[List[str]] = None,
        model_name: str = "sports_model"
    ) -> Dict[str, float]:
        """
        Train a RandomForest model.
        
        Args:
            df: Training data
            target_col: Target column name
            feature_cols: Feature column names (uses all except target if None)
            model_name: Name for saved model
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Starting model training with {len(df)} samples")

        # Prepare data
        if feature_cols is None:
            # Use only numeric feature columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in numeric_cols if col != target_col]
        
        if target_col not in df.columns:
            logger.error(f"Target column '{target_col}' not found")
            return {}

        self.feature_names = feature_cols
        X = df[feature_cols].fillna(0)
        y = df[target_col]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=settings.TEST_SIZE,
            random_state=settings.RANDOM_STATE,
            stratify=y if len(y.unique()) > 1 else None
        )

        logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=settings.RANDOM_FOREST_ESTIMATORS,
            random_state=settings.RANDOM_STATE,
            n_jobs=-1,
            verbose=0
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        }

        # Store metadata
        self.model_metadata = {
            "trained_at": datetime.now().isoformat(),
            "feature_names": feature_cols,
            "target": target_col,
            "samples": len(df),
            "metrics": metrics
        }

        logger.info(f"Model trained. Accuracy: {metrics['accuracy']:.4f}")
        
        # Save model
        self.save(model_name)
        
        return metrics

    def train_advanced(
        self,
        df: pd.DataFrame,
        target_col: str = "home_win",
        feature_cols: Optional[List[str]] = None,
        model_name: str = "sports_model_advanced",
        n_iter: int = 20,
        cv_folds: int = 5,
        scoring: str = "roc_auc"
    ) -> Dict[str, Any]:
        """
        Train with hyperparameter search, cross-validation and probability calibration.
        Returns best CV metrics and saves calibrated model.
        """
        logger.info(f"Starting advanced training with {len(df)} samples")

        if feature_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [c for c in numeric_cols if c != target_col]
        if target_col not in df.columns:
            logger.error(f"Target column '{target_col}' not found")
            return {}

        self.feature_names = feature_cols
        X = df[feature_cols].fillna(0)
        y = df[target_col]

        # Define search space
        param_distributions = {
            "n_estimators": [100, 200, 300, 400, 500],
            "max_depth": [None, 5, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False]
        }

        base_model = RandomForestClassifier(random_state=settings.RANDOM_STATE, n_jobs=-1)

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=settings.RANDOM_STATE)
        search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1,
            random_state=settings.RANDOM_STATE
        )

        search.fit(X, y)
        best_model = search.best_estimator_

        # Probability calibration for better probabilities
        try:
            calibrated = CalibratedClassifierCV(best_model, method="isotonic", cv=cv)
            calibrated.fit(X, y)
            self.model = calibrated
            calibrated_flag = True
        except Exception as e:
            logger.warning(f"Calibration failed, using best model directly: {e}")
            self.model = best_model
            calibrated_flag = False

        # Compute CV-like holdout metrics
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y,
            test_size=settings.TEST_SIZE,
            random_state=settings.RANDOM_STATE,
            stratify=y if len(y.unique()) > 1 else None
        )
        self.model.fit(X_tr, y_tr)
        y_pred = self.model.predict(X_te)
        metrics = {
            "accuracy": float(accuracy_score(y_te, y_pred)),
            "precision": float(precision_score(y_te, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_te, y_pred, average="weighted", zero_division=0)),
            "f1": float(f1_score(y_te, y_pred, average="weighted", zero_division=0)),
            "cv_best_score": float(search.best_score_),
            "calibrated": calibrated_flag,
            "best_params": search.best_params_,
        }

        self.model_metadata = {
            "trained_at": datetime.now().isoformat(),
            "feature_names": feature_cols,
            "target": target_col,
            "samples": len(df),
            "metrics": metrics,
            "best_params": search.best_params_,
            "calibrated": calibrated_flag
        }

        logger.info(f"Advanced model trained. CV best {scoring}: {metrics['cv_best_score']:.4f}")
        self.save(model_name)
        return metrics

    def predict(self, features: List[float]) -> Dict[str, float]:
        """
        Make a prediction for a single sample.
        
        Args:
            features: Feature vector
            
        Returns:
            Dictionary with predicted probabilities
        """
        if self.model is None:
            logger.error("No model loaded")
            return {}

        try:
            # Ensure features is 2D
            features_array = np.array(features).reshape(1, -1)
            
            # Check feature count
            if features_array.shape[1] != len(self.feature_names or []):
                logger.warning(
                    f"Feature count mismatch: got {features_array.shape[1]}, "
                    f"expected {len(self.feature_names or [])}"
                )

            proba = self.model.predict_proba(features_array)[0]
            classes = self.model.classes_

            prediction = {}
            for class_label, prob in zip(classes, proba):
                prediction[f"class_{class_label}_prob"] = float(prob)

            return prediction
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {}

    def predict_batch(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Make predictions for multiple samples.
        
        Args:
            features_df: DataFrame with feature rows
            
        Returns:
            Array of predictions
        """
        if self.model is None:
            logger.error("No model loaded")
            return np.array([])

        try:
            X = features_df.fillna(0)
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return np.array([])

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importances."""
        if self.model is None or self.feature_names is None:
            return {}

        importances = self.model.feature_importances_
        return {
            name: float(importance)
            for name, importance in zip(self.feature_names, importances)
        }

    def save(self, model_name: str = "sports_model") -> bool:
        """
        Save model to disk.
        
        Args:
            model_name: Name for saved model
            
        Returns:
            True if successful
        """
        if self.model is None:
            logger.error("No model to save")
            return False

        try:
            model_path = MODELS_DIR / f"{model_name}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)
            
            # Save metadata
            metadata_path = MODELS_DIR / f"{model_name}_metadata.pkl"
            with open(metadata_path, "wb") as f:
                pickle.dump(self.model_metadata, f)
            
            logger.info(f"Model saved to {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load(self, model_name: str = "sports_model") -> bool:
        """
        Load model from disk.
        
        Args:
            model_name: Name of saved model
            
        Returns:
            True if successful
        """
        try:
            model_path = MODELS_DIR / f"{model_name}.pkl"
            if not model_path.exists():
                logger.error(f"Model not found: {model_path}")
                return False

            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

            # Load metadata if exists
            metadata_path = MODELS_DIR / f"{model_name}_metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, "rb") as f:
                    self.model_metadata = pickle.load(f)
                    self.feature_names = self.model_metadata.get("feature_names")

            logger.info(f"Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class BetAnalyzer:
    """Analyze predictions and identify value bets."""

    @staticmethod
    def calculate_implied_probability(odds: float) -> float:
        """
        Calculate implied probability from decimal odds.
        
        Args:
            odds: Decimal odds
            
        Returns:
            Implied probability (0-1)
        """
        if odds <= 0:
            return 0.0
        return 1.0 / odds

    @staticmethod
    def calculate_expected_value(
        probability: float,
        odds: float,
        stake: float = 1.0
    ) -> float:
        """
        Calculate expected value of a bet.
        
        EV = (Probability × Profit) - ((1 - Probability) × Stake)
        
        Args:
            probability: Predicted probability
            odds: Decimal odds
            stake: Bet stake amount
            
        Returns:
            Expected value
        """
        profit = (odds - 1) * stake
        return (probability * profit) - ((1 - probability) * stake)

    @classmethod
    def find_value_bets(
        cls,
        predictions: Dict[str, float],
        odds: Dict[str, float],
        min_edge: float = None
    ) -> List[Dict[str, Any]]:
        """
        Identify value bets from predictions and odds.
        
        Args:
            predictions: Predicted probabilities
            odds: Betting odds
            min_edge: Minimum edge threshold (default from settings)
            
        Returns:
            List of value bet opportunities
        """
        min_edge = min_edge or settings.EDGE_THRESHOLD
        value_bets = []

        for outcome, odds_value in odds.items():
            # Match outcome with prediction (normalize names)
            pred_key = f"class_{outcome}_prob"
            if pred_key not in predictions:
                continue

            pred_prob = predictions[pred_key]
            implied_prob = cls.calculate_implied_probability(odds_value)
            edge = pred_prob - implied_prob

            if edge > min_edge and pred_prob > settings.MIN_CONFIDENCE:
                ev = cls.calculate_expected_value(pred_prob, odds_value)
                value_bets.append({
                    "outcome": outcome,
                    "odds": odds_value,
                    "predicted_probability": round(pred_prob, 4),
                    "implied_probability": round(implied_prob, 4),
                    "edge": round(edge, 4),
                    "expected_value": round(ev, 4),
                    "recommendation": "STRONG BET" if edge > min_edge * 2 else "BET"
                })

        return sorted(value_bets, key=lambda x: x["edge"], reverse=True)

    @staticmethod
    def calculate_kelly_criterion(
        probability: float,
        odds: float
    ) -> float:
        """
        Calculate Kelly Criterion for optimal bet sizing.
        
        Kelly % = (bp - q) / b
        where b = odds - 1, p = probability, q = 1 - p
        
        Args:
            probability: Predicted probability
            odds: Decimal odds
            
        Returns:
            Recommended bet percentage of bankroll (0-1)
        """
        if odds <= 1 or probability <= 0:
            return 0.0
        
        b = odds - 1
        q = 1 - probability
        kelly = (b * probability - q) / b
        
        # Return full kelly but cap at 25% for safety
        return max(0, min(kelly, 0.25))


# Singleton instance
_model_manager = None


def get_model_manager() -> ModelManager:
    """Get or create model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
