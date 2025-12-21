"""
Integrated Prediction Engine
Combines live betting odds, real-time data, and ML predictions for value bet identification.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from src.predictor import ModelManager
from src.unified_data_source import get_unified_data_manager, UnifiedDataSourceManager
from src.live_sports_data import get_live_fetcher
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class BetRecommendation:
    """Represents a betting recommendation."""
    match_id: str
    home_team: str
    away_team: str
    sport: str
    league: str
    predicted_winner: str
    prediction_confidence: float
    predicted_probability: float
    market_probability: float
    implied_value: float
    recommended_odds: float
    expected_value: float
    edge: float
    recommendation: str  # "STRONG_BUY", "BUY", "HOLD", "SELL", "AVOID"
    live_odds_home: Optional[float] = None
    live_odds_draw: Optional[float] = None
    live_odds_away: Optional[float] = None
    bookmaker: Optional[str] = None


class IntegratedPredictionEngine:
    """
    Combines ML predictions, live data, and betting odds for recommendations.
    Uses real-time sports data and historical analysis for optimal predictions.
    """

    def __init__(self):
        """Initialize prediction engine with data sources."""
        self.model_manager = ModelManager()
        self.data_manager: UnifiedDataSourceManager = get_unified_data_manager()
        self.live_fetcher = get_live_fetcher()
        self.minimum_confidence = settings.MIN_CONFIDENCE
        self.edge_threshold = settings.EDGE_THRESHOLD

    def train_on_live_and_historical(
        self,
        sport: str = "soccer",
        model_name: str = "integrated_model"
    ) -> Dict[str, float]:
        """
        Train model using combined historical and live data.
        
        Args:
            sport: Sport type to train on
            model_name: Name for saved model
            
        Returns:
            Training metrics
        """
        logger.info(f"Training integrated model on {sport} with live + historical data...")
        
        # Get combined training data
        training_df = self.data_manager.get_training_data(
            source="combined",
            sport=sport,
            min_samples=100
        )
        
        if len(training_df) == 0:
            logger.error("No training data available")
            return {}
        
        logger.info(f"Training on {len(training_df)} records")
        
        # Prepare features
        training_df = self._prepare_features(training_df)
        
        # Train model
        metrics = self.model_manager.train(
            training_df,
            target_col="result",
            model_name=model_name
        )
        
        return metrics

    def predict_match(
        self,
        home_team: str,
        away_team: str,
        sport: str = "soccer",
        use_live_data: bool = True
    ) -> Optional[BetRecommendation]:
        """
        Generate bet recommendation for a specific match.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            use_live_data: Whether to use live API data
            
        Returns:
            BetRecommendation object or None
        """
        try:
            logger.info(f"Generating prediction for {home_team} vs {away_team}")
            
            # Get live odds
            live_odds = self.data_manager.get_live_odds(home_team, away_team, sport)
            
            if not live_odds:
                logger.warning("Could not fetch live odds")
                return None
            
            # Extract features from historical data
            features = self.data_manager.get_match_features(
                home_team, away_team, sport
            )
            
            if features is None:
                logger.warning(f"Could not extract features for {home_team} vs {away_team}")
                return None
            
            # Get ML prediction
            ml_prediction = self._get_ml_prediction(features, sport)
            
            if ml_prediction is None:
                return None
            
            # Calculate betting metrics
            recommendation = self._calculate_bet_recommendation(
                home_team, away_team, sport,
                ml_prediction, live_odds
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error predicting match: {e}")
            return None

    def predict_multiple_matches(
        self,
        sport: str = "soccer",
        league: Optional[str] = None,
        min_edge: Optional[float] = None
    ) -> List[BetRecommendation]:
        """
        Generate predictions for all upcoming matches.
        
        Args:
            sport: Sport type
            league: Specific league to focus on
            min_edge: Minimum edge filter
            
        Returns:
            List of BetRecommendation objects
        """
        recommendations = []
        min_edge = min_edge or self.edge_threshold
        
        try:
            # Get all live matches
            live_matches_df = self.live_fetcher.fetch_all_live_matches(
                sports=[sport],
                days_ahead=7
            )
            
            if len(live_matches_df) == 0:
                logger.warning(f"No live matches found for {sport}")
                return recommendations
            
            # Filter by league if specified
            if league:
                live_matches_df = live_matches_df[live_matches_df['league'] == league]
            
            logger.info(f"Found {len(live_matches_df)} matches for prediction")
            
            # Generate predictions for each match
            for _, match in live_matches_df.iterrows():
                recommendation = self.predict_match(
                    match['home_team'],
                    match['away_team'],
                    sport
                )
                
                if recommendation and recommendation.edge >= min_edge:
                    recommendations.append(recommendation)
            
            # Sort by edge (highest first)
            recommendations.sort(key=lambda x: x.edge, reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error predicting multiple matches: {e}")
            return recommendations

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model training."""
        # Fill missing values
        df = df.fillna(0)
        
        # Create target variable if needed
        if 'result' not in df.columns and 'home_score' in df.columns:
            df['result'] = (df['home_score'] > df['away_score']).astype(int)
        
        # Ensure numeric columns
        numeric_cols = ['home_score', 'away_score', 'odds_home', 'odds_draw', 'odds_away']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df

    def _get_ml_prediction(
        self,
        features: Dict[str, float],
        sport: str
    ) -> Optional[Dict[str, Any]]:
        """Get ML model prediction."""
        try:
            # Load model if not already loaded
            if self.model_manager.model is None:
                model_path = f"models/model_{sport}.pkl"
                self.model_manager.load(model_path)
            
            if self.model_manager.model is None:
                logger.warning(f"No trained model for {sport}")
                return None
            
            # Prepare feature vector
            feature_vector = self._create_feature_vector(features)
            
            # Get prediction and probability
            prediction = self.model_manager.model.predict([feature_vector])[0]
            probability = self.model_manager.model.predict_proba([feature_vector])[0][1]
            
            return {
                "prediction": "HOME_WIN" if prediction == 1 else "AWAY_WIN",
                "probability": probability,
                "confidence": max(probability, 1 - probability)
            }
            
        except Exception as e:
            logger.error(f"Error getting ML prediction: {e}")
            return None

    def _create_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Create feature vector for ML model."""
        # Order matters - must match training features
        feature_order = [
            "home_wins", "home_draws", "home_losses",
            "home_goals_for", "home_goals_against",
            "away_wins", "away_draws", "away_losses",
            "away_goals_for", "away_goals_against"
        ]
        
        vector = []
        for feature_name in feature_order:
            vector.append(features.get(feature_name, 0))
        
        return np.array(vector).reshape(1, -1)

    def _calculate_bet_recommendation(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        ml_prediction: Dict[str, Any],
        live_odds: Dict[str, float]
    ) -> Optional[BetRecommendation]:
        """Calculate betting recommendation based on all factors."""
        try:
            ml_prob = ml_prediction["probability"]
            confidence = ml_prediction["confidence"]
            
            # Determine predicted winner
            predicted_winner = "HOME" if ml_prob > 0.5 else "AWAY"
            
            # Get market probability from odds
            odds_home = live_odds.get("home", 1.0)
            odds_away = live_odds.get("away", 1.0)
            
            # Convert odds to implied probability
            market_prob_home = 1.0 / odds_home if odds_home > 1 else 0.5
            market_prob_away = 1.0 / odds_away if odds_away > 1 else 0.5
            
            # Normalize probabilities
            total_prob = market_prob_home + market_prob_away
            market_prob_home = market_prob_home / total_prob if total_prob > 0 else 0.5
            market_prob_away = market_prob_away / total_prob if total_prob > 0 else 0.5
            
            # Calculate value
            if predicted_winner == "HOME":
                recommended_odds = odds_home
                market_probability = market_prob_home
                predicted_prob = ml_prob
            else:
                recommended_odds = odds_away
                market_probability = market_prob_away
                predicted_prob = 1 - ml_prob
            
            # Expected value
            ev = (predicted_prob * recommended_odds) - 1
            
            # Edge
            edge = predicted_prob - market_probability
            
            # Recommendation
            if confidence < self.minimum_confidence:
                recommendation = "AVOID"
            elif edge >= 0.15:
                recommendation = "STRONG_BUY"
            elif edge >= self.edge_threshold:
                recommendation = "BUY"
            elif edge >= 0:
                recommendation = "HOLD"
            elif edge < -0.1:
                recommendation = "SELL"
            else:
                recommendation = "AVOID"
            
            return BetRecommendation(
                match_id=f"{home_team}_{away_team}_{sport}",
                home_team=home_team,
                away_team=away_team,
                sport=sport,
                league="mixed",
                predicted_winner=predicted_winner,
                prediction_confidence=confidence,
                predicted_probability=predicted_prob,
                market_probability=market_probability,
                implied_value=ev,
                recommended_odds=recommended_odds,
                expected_value=ev * recommended_odds,
                edge=edge,
                recommendation=recommendation,
                live_odds_home=live_odds.get("home"),
                live_odds_draw=live_odds.get("draw"),
                live_odds_away=live_odds.get("away"),
                bookmaker=live_odds.get("bookmaker")
            )
            
        except Exception as e:
            logger.error(f"Error calculating bet recommendation: {e}")
            return None

    def get_best_value_bets(
        self,
        sport: str = "soccer",
        top_n: int = 10
    ) -> List[BetRecommendation]:
        """Get top N bets with best value."""
        recommendations = self.predict_multiple_matches(sport=sport)
        
        # Filter for positive edge
        value_bets = [r for r in recommendations if r.edge > 0]
        
        # Sort by edge
        value_bets.sort(key=lambda x: x.edge, reverse=True)
        
        return value_bets[:top_n]

    def generate_report(
        self,
        sport: str = "soccer"
    ) -> Dict[str, Any]:
        """Generate comprehensive betting analysis report."""
        try:
            recommendations = self.predict_multiple_matches(sport=sport)
            value_bets = self.get_best_value_bets(sport=sport)
            
            report = {
                "timestamp": pd.Timestamp.now().isoformat(),
                "sport": sport,
                "total_matches_analyzed": len(recommendations),
                "positive_edge_bets": len(value_bets),
                "best_value_bets": [
                    {
                        "match": f"{b.home_team} vs {b.away_team}",
                        "recommendation": b.recommendation,
                        "predicted_winner": b.predicted_winner,
                        "edge": f"{b.edge:.2%}",
                        "expected_value": f"{b.expected_value:.2f}x",
                        "live_odds": b.live_odds_home or b.live_odds_away,
                        "confidence": f"{b.prediction_confidence:.2%}"
                    }
                    for b in value_bets[:5]
                ],
                "average_edge": np.mean([r.edge for r in recommendations]) if recommendations else 0,
                "average_confidence": np.mean([r.prediction_confidence for r in recommendations]) if recommendations else 0,
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"error": str(e)}


def get_prediction_engine() -> IntegratedPredictionEngine:
    """Get or create singleton instance."""
    return IntegratedPredictionEngine()
