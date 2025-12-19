"""Tests for predictor module."""

import pytest
import pandas as pd
import numpy as np
from src.predictor import ModelManager, BetAnalyzer


class TestModelManager:
    """Test model manager functionality."""

    def test_initialization(self):
        """Test manager initializes correctly."""
        manager = ModelManager()
        assert manager.model is None
        assert manager.feature_names is None

    def test_train(self, sample_data):
        """Test model training."""
        manager = ModelManager()
        metrics = manager.train(sample_data, target_col='home_win')
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert manager.model is not None
        assert manager.feature_names is not None

    def test_predict(self, sample_data):
        """Test prediction."""
        manager = ModelManager()
        manager.train(sample_data, target_col='home_win')
        
        features = [0.7, 0.6, 0.5, 2]  # Match feature count
        prediction = manager.predict(features)
        
        assert prediction
        assert all(0 <= v <= 1 for v in prediction.values())

    def test_predict_batch(self, sample_data):
        """Test batch prediction."""
        manager = ModelManager()
        manager.train(sample_data, target_col='home_win')
        
        features_df = sample_data.drop('home_win', axis=1).head(10)
        predictions = manager.predict_batch(features_df)
        
        assert len(predictions) == 10

    def test_feature_importance(self, sample_data):
        """Test feature importance retrieval."""
        manager = ModelManager()
        manager.train(sample_data, target_col='home_win')
        
        importance = manager.get_feature_importance()
        
        assert importance
        assert len(importance) == len(manager.feature_names)
        assert all(v >= 0 for v in importance.values())

    def test_save_load(self, sample_data, tmp_path):
        """Test model save and load."""
        # Train and save
        manager1 = ModelManager()
        manager1.train(sample_data, target_col='home_win', model_name='test_model')
        
        # Load
        manager2 = ModelManager()
        loaded = manager2.load('test_model')
        assert loaded is True
        assert manager2.model is not None


class TestBetAnalyzer:
    """Test bet analysis functionality."""

    def test_implied_probability(self):
        """Test implied probability calculation."""
        prob = BetAnalyzer.calculate_implied_probability(odds=2.0)
        assert prob == 0.5
        
        prob = BetAnalyzer.calculate_implied_probability(odds=1.5)
        assert abs(prob - 0.667) < 0.01

    def test_expected_value(self):
        """Test expected value calculation."""
        ev = BetAnalyzer.calculate_expected_value(
            probability=0.6,
            odds=2.0,
            stake=100
        )
        # EV = (0.6 * 100) - (0.4 * 100) = 20
        assert ev == 20

    def test_find_value_bets(self, sample_prediction, sample_odds):
        """Test value bet finding."""
        bets = BetAnalyzer.find_value_bets(
            sample_prediction,
            sample_odds,
            min_edge=0.05
        )
        
        # Should find bets or return empty list
        assert isinstance(bets, list)

    def test_kelly_criterion(self):
        """Test Kelly criterion calculation."""
        kelly = BetAnalyzer.calculate_kelly_criterion(
            probability=0.6,
            odds=2.0
        )
        
        assert 0 <= kelly <= 0.25  # Should be within bounds
        assert kelly > 0  # Positive expected value

    def test_kelly_negative_ev(self):
        """Test Kelly for negative EV."""
        kelly = BetAnalyzer.calculate_kelly_criterion(
            probability=0.4,
            odds=2.0
        )
        
        assert kelly == 0  # Should not bet on negative EV


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, sample_data, sample_odds):
        """Test complete prediction workflow."""
        # Train
        manager = ModelManager()
        metrics = manager.train(sample_data, target_col='home_win')
        assert metrics['accuracy'] > 0
        
        # Predict
        features = [0.7, 0.6, 0.5, 2]
        prediction = manager.predict(features)
        assert prediction
        
        # Analyze
        bets = BetAnalyzer.find_value_bets(prediction, sample_odds)
        assert isinstance(bets, list)
