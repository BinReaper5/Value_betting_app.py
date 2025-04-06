
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Config
API_KEY = '6328c8912f177fcaf269a6822fe04006'
BASE_URL = 'https://api.the-odds-api.com/v4/sports/'

# Team logo mappings (partial examples — add more as needed)
TEAM_LOGOS = {
    "New York Yankees": "https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png",
    "Boston Red Sox": "https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
}

st.set_page_config(page_title="Value Betting App", layout="wide")
st.title("**Value Betting Dashboard**")
st.markdown("Live MLB & NBA odds, team logos, value alerts, and filters.")

tabs_titles = ["MLB Odds", "NBA Odds"]
tabs = st.tabs(tabs_titles)
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
        return round(100 / (odds + 100) * 100, 1)
    else:
        return round(-odds / (-odds + 100) * 100, 1)

def display_odds(odds_data, sport_name):
    rows = []
    for game in odds_data:
        try:
            game_info = {
                "Matchup": f"{game['away_team']} @ {game['home_team']}",
                "Start Time (UTC)": datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d %I:%M %p")
            }
            home = game['home_team']
            away = game['away_team']

            game_info["Home Logo"] = TEAM_LOGOS.get(home, "")
            game_info["Away Logo"] = TEAM_LOGOS.get(away, "")

            if game['bookmakers']:
                market = game['bookmakers'][0]['markets'][0]
                for outcome in market['outcomes']:
                    if outcome['name'] == home:
                        game_info["Home Odds"] = outcome['price']
                        game_info["Home Implied %"] = american_to_implied(outcome['price'])
                    elif outcome['name'] == away:
                        game_info["Away Odds"] = outcome['price']
                        game_info["Away Implied %"] = american_to_implied(outcome['price'])

            # Add mock model values
            game_info["Model Home %"] = 55
            game_info["Model Away %"] = 45
            game_info["Home Value"] = round(game_info["Model Home %"] - game_info.get("Home Implied %", 0), 1)
            game_info["Away Value"] = round(game_info["Model Away %"] - game_info.get("Away Implied %", 0), 1)

            rows.append(game_info)
        except Exception as e:
            print(f"Skipped a game due to error: {e}")
            continue

    df = pd.DataFrame(rows)

    # Team Filter
    teams = sorted(set(df["Matchup"].str.extractall(r'([A-Za-z ]+)')[0].dropna().unique()))
    selected_team = st.selectbox(f"Filter by Team ({sport_name})", ["All"] + teams)
    if selected_team != "All":
        df = df[df["Matchup"].str.contains(selected_team)]

    # Reorder and display
    display_df = df[[
        "Matchup", "Start Time (UTC)",
        "Away Logo", "Away Odds", "Away Implied %", "Model Away %", "Away Value",
        "Home Logo", "Home Odds", "Home Implied %", "Model Home %", "Home Value"
    ]].copy()

    def highlight_value(val):
        if val > 3:
            return "background-color: #b6fcb6"
        elif val < -3:
            return "background-color: #ffb6b6"
        else:
            return ""

    st.dataframe(display_df.style.applymap(highlight_value, subset=["Away Value", "Home Value"]), use_container_width=True)

# Render tabs
for tab, sport_key, tab_title in zip(tabs, sport_map.values(), tabs_titles):
    with tab:
        odds = fetch_odds(sport_key)
        if odds:
            display_odds(odds, tab_title)
