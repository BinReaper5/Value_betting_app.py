
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# App Config
API_KEY = '6328c8912f177fcaf269a6822fe04006'
BASE_URL = 'https://api.the-odds-api.com/v4/sports/'

st.set_page_config(page_title="Value Betting App", layout="wide")
st.title("**Value Betting Dashboard**")
st.markdown("Get real-time MLB and NBA odds, implied probabilities, and flag potential value bets.")

# Tab Setup
tabs = st.tabs(["MLB Odds", "NBA Odds"])

sport_map = {"MLB Odds": "baseball_mlb", "NBA Odds": "basketball_nba"}

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
        st.error(f"API Error {response.status_code}: {response.text}")
        return []

def american_to_implied(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

def display_odds(odds_data):
    rows = []
    for game in odds_data:
        game_info = {
            "Matchup": f"{game['away_team']} @ {game['home_team']}",
            "Start Time (UTC)": datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d %I:%M %p")
        }
        if game['bookmakers']:
            market = game['bookmakers'][0]['markets'][0]
            for outcome in market['outcomes']:
                if outcome['name'] == game['home_team']:
                    game_info["Home Team"] = game['home_team']
                    game_info["Home Odds"] = outcome['price']
                    game_info["Home Implied %"] = round(american_to_implied(outcome['price']) * 100, 1)
                elif outcome['name'] == game['away_team']:
                    game_info["Away Team"] = game['away_team']
                    game_info["Away Odds"] = outcome['price']
                    game_info["Away Implied %"] = round(american_to_implied(outcome['price']) * 100, 1)
        rows.append(game_info)
    df = pd.DataFrame(rows)
    return df

# Loop through each tab and display odds
for tab, sport_key in zip(tabs, sport_map.values()):
    with tab:
        st.subheader(f"Live {sport_key.split('_')[1].upper()} Odds")
        data = fetch_odds(sport_key)
        if data:
            df = display_odds(data)
            st.dataframe(df, use_container_width=True)
