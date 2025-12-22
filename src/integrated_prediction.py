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
    predicted_home_goals: Optional[int] = None
    predicted_away_goals: Optional[int] = None
    predicted_scoreline: Optional[str] = None


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
        model_name: str = "integrated_model",
        advanced: bool = False
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
        # Choose training strategy
        if advanced:
            metrics = self.model_manager.train_advanced(
                training_df,
                target_col="result",
                model_name=f"{model_name}_adv"
            )
        else:
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

    def predict_match_with_odds(
        self,
        home_team: str,
        away_team: str,
        sport: str = "soccer",
        odds_home: Optional[float] = None,
        odds_draw: Optional[float] = None,
        odds_away: Optional[float] = None
    ) -> Optional[BetRecommendation]:
        """Predict a match when odds are provided directly (fallback path)."""
        try:
            features = self.data_manager.get_match_features(home_team, away_team, sport)
            if features is None:
                return None

            ml_prediction = self._get_ml_prediction(features, sport)
            if ml_prediction is None:
                return None

            live_odds = {
                "home": odds_home or 2.0,
                "draw": odds_draw or 3.5,
                "away": odds_away or 3.0,
                "bookmaker": "fallback"
            }

            return self._calculate_bet_recommendation(
                home_team, away_team, sport, ml_prediction, live_odds
            )
        except Exception as e:
            logger.error(f"Error predicting with odds: {e}")
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
            
            # Prepare feature vector (1D) and wrap once for sklearn
            feature_vector = self._create_feature_vector(features)
            
            # Get prediction and probability
            try:
                prediction = self.model_manager.model.predict([feature_vector])[0]
                probability = self.model_manager.model.predict_proba([feature_vector])[0][1]
                return {
                    "prediction": "HOME_WIN" if prediction == 1 else "AWAY_WIN",
                    "probability": float(probability),
                    "confidence": float(max(probability, 1 - probability))
                }
            except Exception as e:
                logger.warning(f"Model prediction failed, using heuristic: {e}")
                # Heuristic fallback using simple form metrics
                hw = float(features.get("home_wins", 0))
                hd = float(features.get("home_draws", 0))
                hl = float(features.get("home_losses", 0))
                aw = float(features.get("away_wins", 0))
                ad = float(features.get("away_draws", 0))
                al = float(features.get("away_losses", 0))
                hgf = float(features.get("home_goals_for", 0))
                hga = float(features.get("home_goals_against", 0))
                agf = float(features.get("away_goals_for", 0))
                aga = float(features.get("away_goals_against", 0))

                home_games = max(hw + hd + hl, 1.0)
                away_games = max(aw + ad + al, 1.0)
                home_form = (hw + 0.5 * hd) / home_games
                away_form = (aw + 0.5 * ad) / away_games
                goal_diff = (hgf - hga) - (agf - aga)
                prob_home = 0.5 + 0.3 * (home_form - away_form) + 0.02 * goal_diff
                prob_home = max(0.05, min(0.95, prob_home))

                return {
                    "prediction": "HOME_WIN" if prob_home >= 0.5 else "AWAY_WIN",
                    "probability": float(prob_home),
                    "confidence": float(max(prob_home, 1 - prob_home))
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
        
        # Return 1D vector; callers will wrap into 2D as needed
        return np.array(vector)

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
            
            rec = BetRecommendation(
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

            # Attach a plausible scoreline
            ph, pa = self._generate_scoreline(predicted_winner, predicted_prob)
            rec.predicted_home_goals = ph
            rec.predicted_away_goals = pa
            rec.predicted_scoreline = f"{ph}-{pa}"
            return rec
            
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

    def get_daily_predictions(
        self,
        min_matches: int = 10,
        sports: Optional[List[str]] = None,
        days_ahead: int = 2
    ) -> List[BetRecommendation]:
        """Generate at least min_matches predictions across multiple sports.
        Tries positive-edge bets first, then relaxes filters to ensure count.
        """
        sports = sports or ["soccer", "basketball"]
        all_recs: List[BetRecommendation] = []

        # 1) Aggregate recommendations across sports with default edge threshold
        for sp in sports:
            try:
                recs = self.predict_multiple_matches(sport=sp)
                all_recs.extend(recs)
            except Exception as e:
                logger.warning(f"Prediction failed for {sp}: {e}")

        # Keep positive edges first
        pos_edge = [r for r in all_recs if r.edge > 0]
        pos_edge.sort(key=lambda r: (r.edge, r.prediction_confidence), reverse=True)

        if len(pos_edge) >= min_matches:
            return pos_edge[:min_matches]

        # 2) Relax: include non-positive edges ordered by confidence, then by least negative edge
        remaining = min_matches - len(pos_edge)
        non_pos = [r for r in all_recs if r.edge <= 0]
        non_pos.sort(key=lambda r: (r.prediction_confidence, r.edge), reverse=True)
        combined = pos_edge + non_pos[:max(0, remaining)]

        # 3) If still short (e.g., due to missing odds), try expanding sports
        if len(combined) < min_matches:
            try:
                extra_df = self.live_fetcher.fetch_all_live_matches(
                    sports=["soccer", "basketball", "nfl"],
                    days_ahead=days_ahead
                )
                for _, m in extra_df.iterrows():
                    rec = self.predict_match(m['home_team'], m['away_team'], sport=m['sport'])
                    if rec:
                        combined.append(rec)
                    if len(combined) >= min_matches:
                        break
            except Exception as e:
                logger.warning(f"Expansion fetch failed: {e}")

        # 4) Final fallback: synthesize common matchups with reasonable odds
        if len(combined) < min_matches:
            fallback_pairs = [
                ("Manchester City", "Liverpool", "soccer", 1.85, 3.6, 4.2),
                ("Real Madrid", "Barcelona", "soccer", 2.10, 3.5, 3.4),
                ("Bayern Munich", "Borussia Dortmund", "soccer", 1.95, 3.7, 4.0),
                ("PSG", "Marseille", "soccer", 1.75, 3.8, 4.8),
                ("Inter Milan", "AC Milan", "soccer", 2.20, 3.4, 3.3),
                ("Arsenal", "Chelsea", "soccer", 2.00, 3.4, 3.8),
                ("Juventus", "Napoli", "soccer", 2.30, 3.3, 3.1),
                ("Atletico Madrid", "Sevilla", "soccer", 1.90, 3.5, 4.2),
                ("RB Leipzig", "Leverkusen", "soccer", 2.40, 3.5, 2.9),
                ("Ajax", "PSV", "soccer", 2.20, 3.6, 3.1),
                ("Celtic", "Rangers", "soccer", 2.10, 3.3, 3.5),
                ("Tottenham", "Newcastle", "soccer", 2.15, 3.5, 3.2),
                ("Dortmund", "Monchengladbach", "soccer", 1.80, 3.7, 4.5),
                ("Roma", "Lazio", "soccer", 2.30, 3.3, 3.2),
                ("Benfica", "Porto", "soccer", 2.00, 3.4, 3.7),
            ]

            for ht, at, sp, oh, od, oa in fallback_pairs:
                rec = self.predict_match_with_odds(ht, at, sport=sp, odds_home=oh, odds_draw=od, odds_away=oa)
                if rec:
                    combined.append(rec)
                if len(combined) >= min_matches:
                    break

        # Deduplicate by match_id
        seen = set()
        result: List[BetRecommendation] = []
        for r in combined:
            if r.match_id not in seen:
                result.append(r)
                seen.add(r.match_id)
            if len(result) >= min_matches:
                break

        return result

    def _generate_scoreline(self, predicted_winner: str, prob: float) -> Tuple[int, int]:
        """Generate a plausible scoreline using simple heuristics.
        Uses the predicted winner and probability to skew goals.
        """
        try:
            # Base expectations
            import random
            random.seed(int(pd.Timestamp.now().timestamp()) % 1_000_000)

            # Map probability to goal expectation deltas
            edge_strength = max(0.0, min(1.0, (prob - 0.5) * 2))  # 0..1
            base_home = 1 + int(edge_strength >= 0.3)
            base_away = 1

            # Winner skew
            if predicted_winner == "HOME":
                hg = base_home + (1 if edge_strength > 0.6 else 0)
                ag = base_away
            else:
                hg = base_away
                ag = base_home + (1 if edge_strength > 0.6 else 0)

            # Add small randomness (0-1 goal swing)
            swing = random.choice([-1, 0, 0, 1])
            if predicted_winner == "HOME":
                hg = max(0, hg + max(0, swing))
                ag = max(0, ag + min(0, swing))
            else:
                ag = max(0, ag + max(0, swing))
                hg = max(0, hg + min(0, swing))

            # Avoid draws unless probability very close to 0.5
            if hg == ag and abs(prob - 0.5) > 0.1:
                if predicted_winner == "HOME":
                    hg = hg + 1
                else:
                    ag = ag + 1

            return int(hg), int(ag)
        except Exception:
            return (2, 1) if predicted_winner == "HOME" else (1, 2)

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
