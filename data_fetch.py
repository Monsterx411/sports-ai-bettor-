import requests
import pandas as pd

# Replace with your keys
API_SPORTS_KEY = 'YOUR_API_SPORTS_KEY'
ODDS_API_KEY = 'YOUR_ODDS_API_KEY'

def fetch_fixtures(sport='soccer', league='premier_league'):
    url = f"https://api.api-sports.io/v3/fixtures?league={league}&season=2025"
    headers = {'x-apisports-key': API_SPORTS_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['response']
        return pd.DataFrame([{
            'home': f['teams']['home']['name'],
            'away': f['teams']['away']['name'],
            'date': f['fixture']['date']
        } for f in data])
    return pd.DataFrame()

def fetch_odds(event_id):
    url = f"https://api.the-odds-api.com/v4/sports/soccer/events/{event_id}/odds?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    response = requests.get(url)
    if response.status_code == 200:
        odds = response.json()['bookmakers'][0]['markets'][0]['outcomes']
        return {o['name']: o['price'] for o in odds}
    return {}

# Example: df = fetch_fixtures()
# odds = fetch_odds('some_event_id')  # Get event_id from fixtures