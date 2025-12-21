"""
Web dashboard for Sports AI Bettor using Streamlit.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime

from config.settings import settings
from src.logger import setup_logger
from src.data_fetch import get_fetcher
from src.predictor import get_model_manager, BetAnalyzer
from src.utils import format_percentage

logger = setup_logger(__name__)

# Page config
st.set_page_config(
    page_title="Sports AI Bettor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.markdown("# ⚙️ Settings")
    sport = st.selectbox(
        "Sport",
        ["soccer", "basketball", "nfl"],
        help="Select the sport to analyze"
    )
    league = st.text_input("League", value="premier_league")
    
    st.markdown("---")
    st.markdown("### Model Settings")
    model_name = st.text_input("Model Name", value="sports_model")
    confidence_threshold = st.slider(
        "Confidence Threshold",
        0.0, 1.0, float(settings.MIN_CONFIDENCE),
        step=0.05,
        help="Minimum confidence for predictions"
    )
    edge_threshold = st.slider(
        "Edge Threshold",
        0.0, 0.5, float(settings.EDGE_THRESHOLD),
        step=0.01,
        help="Minimum edge for value bets"
    )

# Main page
st.markdown("# 🎯 Sports AI Bettor")
st.markdown("AI-powered sports betting predictions and value bet analysis")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Fixtures", "🔮 Predictions", "💰 Value Bets", "📈 Analytics"]
)

with tab1:
    st.markdown("## Upcoming Fixtures")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Refresh Fixtures", key="refresh_fixtures"):
            fetcher = get_fetcher()
            fetcher.clear_cache()
            st.rerun()
    
    with st.spinner("Loading fixtures..."):
        fetcher = get_fetcher()
        fixtures_df = fetcher.fetch_fixtures(sport=sport, league=league)
    
    if not fixtures_df.empty:
        # Format dates
        if "date" in fixtures_df.columns:
            fixtures_df["date"] = pd.to_datetime(fixtures_df["date"]).dt.strftime("%Y-%m-%d %H:%M")
        
        st.dataframe(
            fixtures_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "fixture_id": st.column_config.NumberColumn("ID", width="small"),
                "date": st.column_config.TextColumn("Date"),
                "home_team": st.column_config.TextColumn("Home"),
                "away_team": st.column_config.TextColumn("Away"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        st.success(f"✅ Found {len(fixtures_df)} fixtures")
    else:
        st.warning("⚠️ No fixtures found")

with tab2:
    st.markdown("## Make Predictions")
    
    col1, col2 = st.columns(2)
    with col1:
        match_name = st.text_input(
            "Match",
            placeholder="e.g., Arsenal vs Manchester United"
        )
    
    with col2:
        st.markdown("### Feature Values")
    
    # Feature inputs (example)
    col1, col2, col3 = st.columns(3)
    with col1:
        home_form = st.slider("Home Form", 0.0, 1.0, 0.7)
    with col2:
        away_form = st.slider("Away Form", 0.0, 1.0, 0.6)
    with col3:
        home_advantage = st.slider("Home Advantage", 0.0, 1.0, 0.5)
    
    if st.button("🔮 Predict", type="primary"):
        with st.spinner("Making prediction..."):
            manager = get_model_manager()
            if manager.load(model_name):
                features = [home_form, away_form, home_advantage]
                prediction = manager.predict(features)
                
                if prediction:
                    st.markdown("### Prediction Results")
                    
                    cols = st.columns(len(prediction))
                    for col, (key, value) in zip(cols, prediction.items()):
                        with col:
                            st.metric(key, format_percentage(value))
                    
                    # Visualization
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(prediction.keys()),
                            y=list(prediction.values()),
                            marker_color="rgb(55, 83, 109)"
                        )
                    ])
                    fig.update_layout(
                        title="Prediction Probabilities",
                        xaxis_title="Outcome",
                        yaxis_title="Probability",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ Prediction failed")
            else:
                st.error(f"❌ Could not load model: {model_name}")

with tab3:
    st.markdown("## Value Bet Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        odds_home = st.number_input("Home Odds", value=1.80, step=0.01, min_value=1.0)
    with col2:
        odds_draw = st.number_input("Draw Odds", value=3.50, step=0.01, min_value=1.0)
    with col3:
        odds_away = st.number_input("Away Odds", value=4.00, step=0.01, min_value=1.0)
    
    if st.button("💰 Find Value Bets", type="primary"):
        with st.spinner("Analyzing..."):
            manager = get_model_manager()
            if manager.load(model_name):
                # Mock prediction
                features = [0.7, 0.6, 0.5]
                prediction = manager.predict(features)
                
                odds_dict = {
                    "Home": odds_home,
                    "Draw": odds_draw,
                    "Away": odds_away
                }
                
                value_bets = BetAnalyzer.find_value_bets(
                    prediction,
                    odds_dict,
                    min_edge=edge_threshold
                )
                
                if value_bets:
                    for bet in value_bets:
                        with st.container(border=True):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Outcome", bet["outcome"])
                            with col2:
                                st.metric("Odds", f"{bet['odds']:.2f}")
                            with col3:
                                st.metric(
                                    "Edge",
                                    format_percentage(bet["edge"]),
                                    delta=f"{bet['edge']:.1%}"
                                )
                            with col4:
                                recommendation = bet["recommendation"]
                                color = "🟢" if recommendation == "STRONG BET" else "🟡"
                                st.metric("Rating", f"{color} {recommendation}")
                else:
                    st.info("ℹ️ No value bets found with current odds")
            else:
                st.error(f"❌ Could not load model: {model_name}")

with tab4:
    st.markdown("## Analytics & Model Info")
    
    manager = get_model_manager()
    if manager.load(model_name):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Model Metadata")
            if manager.model_metadata:
                st.info(f"✅ Model loaded: {model_name}")
                st.json(manager.model_metadata)
            else:
                st.warning("⚠️ No metadata available")
        
        with col2:
            st.markdown("### Feature Importance")
            importances = manager.get_feature_importance()
            if importances:
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(importances.values()),
                        y=list(importances.keys()),
                        orientation="h"
                    )
                ])
                fig.update_layout(
                    title="Feature Importance",
                    xaxis_title="Importance",
                    yaxis_title="Feature",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"⚠️ Model not found: {model_name}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Environment:** {settings.ENVIRONMENT}")
with col2:
    st.markdown(f"**Cache:** {'Enabled' if settings.CACHE_ENABLED else 'Disabled'}")
with col3:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")