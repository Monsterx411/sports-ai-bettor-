#!/usr/bin/env python3
"""
Command-line interface for Sports AI Bettor.
"""

import sys
import click
import pandas as pd
from pathlib import Path
from typing import Optional

from config.settings import settings, DATA_DIR
from src.logger import setup_logger
from src.data_fetch import get_fetcher
from src.predictor import get_model_manager, BetAnalyzer
from src.utils import format_percentage, export_json

logger = setup_logger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
def cli(debug: bool) -> None:
    """Sports AI Bettor - AI-powered sports betting predictions."""
    if debug:
        logger.setLevel("DEBUG")
        logger.debug("Debug mode enabled")


@cli.command()
@click.option("--sport", default="soccer", help="Sport type")
@click.option("--league", default="premier_league", help="League")
@click.option("--output", type=click.Path(), help="Output file (optional)")
def fixtures(sport: str, league: str, output: Optional[str]) -> None:
    """Fetch upcoming fixtures."""
    click.echo(f"📊 Fetching {sport} fixtures for {league}...")
    
    fetcher = get_fetcher()
    df = fetcher.fetch_fixtures(sport=sport, league=league)
    
    if df.empty:
        click.echo("❌ No fixtures found")
        return

    click.echo(f"\n✅ Found {len(df)} fixtures:\n")
    click.echo(df.to_string(index=False))

    if output:
        df.to_csv(output, index=False)
        click.echo(f"\n✅ Saved to {output}")


@cli.command()
@click.option("--data-file", type=click.Path(exists=True), required=True, help="Training data CSV")
@click.option("--target", default="home_win", help="Target column")
@click.option("--model-name", default="sports_model", help="Model name")
def train(data_file: str, target: str, model_name: str) -> None:
    """Train prediction model."""
    click.echo(f"🤖 Training model: {model_name}")
    
    try:
        df = pd.read_csv(data_file)
        click.echo(f"✅ Loaded {len(df)} samples from {data_file}")

        manager = get_model_manager()
        metrics = manager.train(df, target_col=target, model_name=model_name)

        if metrics:
            click.echo("\n📈 Training Results:")
            click.echo(f"  Accuracy:  {format_percentage(metrics['accuracy'])}")
            click.echo(f"  Precision: {format_percentage(metrics['precision'])}")
            click.echo(f"  Recall:    {format_percentage(metrics['recall'])}")
            click.echo(f"  F1 Score:  {format_percentage(metrics['f1'])}")
        else:
            click.echo("❌ Training failed")
            sys.exit(1)

    except FileNotFoundError:
        click.echo(f"❌ File not found: {data_file}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        logger.exception("Training error")
        sys.exit(1)


@cli.command()
@click.option("--model-name", default="sports_model", help="Model name to load")
@click.argument("features", nargs=-1, type=float, required=True)
def predict(model_name: str, features: tuple) -> None:
    """Make a prediction.
    
    Example: cli_app.py predict 0.7 0.6 0.5 2 8 5 62 38
    """
    click.echo(f"🔮 Making prediction with {model_name}...")
    click.echo(f"📊 Features: {list(features)}")

    
    manager = get_model_manager()
    if not manager.load(model_name):
        click.echo("❌ Failed to load model")
        sys.exit(1)

    prediction = manager.predict(list(features))
    
    if prediction:
        click.echo("\n📊 Predictions:")
        for key, value in prediction.items():
            click.echo(f"  {key}: {format_percentage(value)}")
    else:
        click.echo("❌ Prediction failed")
        sys.exit(1)


@cli.command()
@click.option("--event-id", required=True, help="Event ID")
@click.option("--odds", type=float, nargs=2, multiple=True, required=True,
              help="Outcome and odds pairs (e.g., --odds Home 1.5 --odds Away 2.5)")
@click.option("--model-name", default="sports_model", help="Model name")
@click.option("--output", type=click.Path(), help="Output JSON file (optional)")
def analyze(event_id: str, odds: tuple, model_name: str, output: Optional[str]) -> None:
    """Analyze a match and find value bets."""
    click.echo(f"📊 Analyzing event: {event_id}")

    # Load model
    manager = get_model_manager()
    if not manager.load(model_name):
        click.echo("❌ Failed to load model")
        sys.exit(1)

    # Prepare odds dictionary
    odds_dict = {outcome: price for outcome, price in odds}
    click.echo(f"📈 Odds: {odds_dict}")

    # Make prediction (mock - replace with actual feature extraction)
    features = [0.7, 0.6]  # Placeholder
    predictions = manager.predict(features)

    if not predictions:
        click.echo("❌ Prediction failed")
        sys.exit(1)

    # Find value bets
    value_bets = BetAnalyzer.find_value_bets(predictions, odds_dict)

    click.echo("\n💰 Value Bets Found:")
    if value_bets:
        for bet in value_bets:
            click.echo(f"\n  Outcome: {bet['outcome']}")
            click.echo(f"    Odds: {bet['odds']}")
            click.echo(f"    Predicted Prob: {format_percentage(bet['predicted_probability'])}")
            click.echo(f"    Edge: {format_percentage(bet['edge'])}")
            click.echo(f"    Recommendation: {bet['recommendation']}")
    else:
        click.echo("  No value bets found")

    if output:
        export_json({"event_id": event_id, "bets": value_bets}, output)
        click.echo(f"\n✅ Results saved to {output}")


@cli.command()
def settings_cmd() -> None:
    """Display application settings."""
    click.echo("\n⚙️  Application Settings:")
    click.echo(f"  Environment: {settings.ENVIRONMENT}")
    click.echo(f"  Log Level: {settings.LOG_LEVEL}")
    click.echo(f"  Cache Enabled: {settings.CACHE_ENABLED}")
    click.echo(f"  Edge Threshold: {format_percentage(settings.EDGE_THRESHOLD)}")
    click.echo(f"  Min Confidence: {format_percentage(settings.MIN_CONFIDENCE)}")
    click.echo(f"  Random Forest Estimators: {settings.RANDOM_FOREST_ESTIMATORS}")


@cli.command()
def version() -> None:
    """Show version information."""
    from src import __version__
    click.echo(f"Sports AI Bettor v{__version__}")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  Interrupted")
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        logger.exception("CLI error")
        sys.exit(1)