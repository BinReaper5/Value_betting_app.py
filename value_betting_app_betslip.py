
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_KEY = '6328c8912f177fcaf269a6822fe04006'
BASE_URL = 'https://api.the-odds-api.com/v4/sports/'

TEAM_LOGOS = {
    "New York Yankees": "https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png",
    "Boston Red Sox": "https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
}

st.set_page_config(page_title="Betting App", layout="wide")
st.title("**Live Betting Dashboard with Bet Slip**")

tabs_titles = ["MLB Odds", "NBA Odds"]
tabs = st.tabs(tabs_titles)
sport_map = {"MLB Odds": "baseball_mlb", "NBA Odds": "basketball_nba"}

if "bet_slip" not in st.session_state:
    st.session_state.bet_slip = []

def fetch_odds(sport_key):
    url = f"{BASE_URL}{sport_key}/odds/"
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def american_to_decimal(odds):
    return round((odds / 100 + 1) if odds > 0 else (100 / abs(odds) + 1), 2)

def display_odds(odds_data, sport_name):
    for game in odds_data:
        try:
            home = game['home_team']
            away = game['away_team']
            matchup = f"{away} @ {home}"
            start_time = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d %I:%M %p")
            odds = {outcome['name']: outcome['price'] for outcome in game['bookmakers'][0]['markets'][0]['outcomes']}

            with st.container():
                st.markdown(f"### {matchup}")
                st.markdown(f"**Start Time:** {start_time}")
                col1, col2 = st.columns(2)

                with col1:
                    st.image(TEAM_LOGOS.get(away, ""), width=50)
                    st.write(f"{away} Odds: {odds.get(away)}")
                    if st.button(f"Add {away}", key=f"{matchup}_{away}"):
                        st.session_state.bet_slip.append({"Team": away, "Odds": odds.get(away), "Matchup": matchup})

                with col2:
                    st.image(TEAM_LOGOS.get(home, ""), width=50)
                    st.write(f"{home} Odds: {odds.get(home)}")
                    if st.button(f"Add {home}", key=f"{matchup}_{home}"):
                        st.session_state.bet_slip.append({"Team": home, "Odds": odds.get(home), "Matchup": matchup})

                st.divider()

        except Exception as e:
            continue

# Bet Slip Sidebar
with st.sidebar:
    st.header("My Bet Slip")
    if st.session_state.bet_slip:
        total_odds = 1.0
        for i, pick in enumerate(st.session_state.bet_slip):
            dec_odds = american_to_decimal(pick["Odds"])
            total_odds *= dec_odds
            st.write(f"{pick['Team']} ({pick['Odds']}) - {pick['Matchup']}")
            if st.button(f"Remove {pick['Team']} - {i}", key=f"remove_{i}"):
                st.session_state.bet_slip.pop(i)
                st.experimental_rerun()

        bet_amt = st.number_input("Bet Amount ($)", min_value=1, value=10)
        potential_win = round(bet_amt * total_odds, 2)
        st.write(f"**Parlay Odds:** {round(total_odds, 2)}")
        st.write(f"**Payout:** ${potential_win}")
        if st.button("Clear Slip"):
            st.session_state.bet_slip = []
            st.experimental_rerun()
    else:
        st.write("No picks added yet.")

# Display odds in tabs
for tab, sport_key, title in zip(tabs, sport_map.values(), tabs_titles):
    with tab:
        data = fetch_odds(sport_key)
        if data:
            display_odds(data, title)
