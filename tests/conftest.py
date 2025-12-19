"""Test configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_data():
    """Create sample training data."""
    np.random.seed(42)
    return pd.DataFrame({
        'home_form': np.random.uniform(0, 1, 100),
        'away_form': np.random.uniform(0, 1, 100),
        'home_advantage': np.random.uniform(0, 1, 100),
        'recent_goals': np.random.randint(0, 5, 100),
        'home_win': np.random.randint(0, 2, 100)
    })


@pytest.fixture
def sample_odds():
    """Create sample odds data."""
    return {
        'Home': 1.80,
        'Draw': 3.50,
        'Away': 4.00
    }


@pytest.fixture
def sample_prediction():
    """Create sample prediction output."""
    return {
        'class_0_prob': 0.35,  # Away win
        'class_1_prob': 0.50,  # Home win
        'class_2_prob': 0.15   # Draw
    }
