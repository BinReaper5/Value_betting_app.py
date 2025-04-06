
import streamlit as st
import pandas as pd
import requests

# Config
API_KEY = '6328c8912f177fcaf269a6822fe04006'
BASE_URL = 'https://api.the-odds-api.com/v4/sports/'

st.title("MLB & NBA Value Betting Model")

sport_choice = st.selectbox("Choose a Sport", ["MLB", "NBA"])

# Map sport choice to API key
sport_key_map = {
    "MLB": "baseball_mlb",
    "NBA": "basketball_nba"
}

def fetch_odds(sport_key):
    url = f"{BASE_URL}{sport_key}/odds/"
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return []

def display_games(data):
    rows = []
    for game in data:
        info = {
            "Game": f"{game['away_team']} @ {game['home_team']}",
            "Start Time": game['commence_time']
        }
        if game['bookmakers']:
            for market in game['bookmakers'][0]['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == game['home_team']:
                            info["Home Odds"] = outcome['price']
                        elif outcome['name'] == game['away_team']:
                            info["Away Odds"] = outcome['price']
        rows.append(info)
    df = pd.DataFrame(rows)
    st.dataframe(df)

# Run app logic
if sport_choice:
    sport_key = sport_key_map[sport_choice]
    odds_data = fetch_odds(sport_key)
    if odds_data:
        display_games(odds_data)
