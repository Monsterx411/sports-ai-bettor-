import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from data_fetch import fetch_fixtures, fetch_odds  # Import from above

def train_model(historical_df):
    # Assume historical_df has columns: 'home_win' (1/0), features like 'home_form', 'away_form', etc.
    X = historical_df.drop('home_win', axis=1)
    y = historical_df['home_win']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test))}")
    return model

def predict_outcome(model, features):
    prob = model.predict_proba([features])[0]  # [loss_prob, draw_prob, win_prob]
    return {'home_win_prob': prob[1], 'draw_prob': prob[0], 'away_win_prob': prob[2] if len(prob) > 2 else 0}

# Example: Load historical data (prepare your CSV)
# historical_df = pd.read_csv('historical_soccer.csv')
# model = train_model(historical_df)
# pred = predict_outcome(model, [some_features_vector])

def generate_bets(pred, odds):
    implied_prob = 1 / odds.get('home', 1)  # Simplified
    if pred['home_win_prob'] > implied_prob + 0.05:  # 5% edge
        return f"Value bet: Home win at {odds['home']} odds"
    # Add for draw/away
    return "No value bets"