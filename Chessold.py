# Let's start developing your Streamlit app together.
# Below is a basic outline of a Streamlit application for saving and tracking chess match scores.

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Replace 'your_json_keyfile.json' with the path to your credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/acolla/Projects/CHESS_TRACKER/chessscore-440310-4073b5fa8961.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet (replace 'Chess Championship Data' with the name of your sheet)
sheet = client.open("Chess Championship Data").sheet1

# Title and Introduction
st.title('Chess Championship Tracker')
st.write("""
Welcome to the Chess Championship Tracker!
Use this application to save and track the scores of your chess matches.
Create championships, log match results, and compare overall scores between players.
""")

# Sidebar Setup
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the options below to explore the app.")

# Initialising session state to store data
if 'championships' not in st.session_state:
    st.session_state['championships'] = []
    # Load data from Google Sheets if available
    rows = sheet.get_all_records(expected_headers=["Championship Name", "Winner", "Winner Colour", "Date"])
    for row in rows:
        if row['Championship Name'] not in [c['name'] for c in st.session_state['championships']]:
            st.session_state['championships'].append({
                'name': row['Championship Name'],
                'matches': []
            })
        # Add match details to the respective championship
        for champ in st.session_state['championships']:
            if champ['name'] == row['Championship Name']:
                champ['matches'].append({
                    'winner': row['Winner'],
                    'colour': row['Winner Colour'],
                    'date': row['Date']
                })

# Adding a new championship
st.sidebar.header("Add New Championship")
championship_name = st.sidebar.text_input("Championship Name")
player_name_1 = st.sidebar.text_input("Player 1 Name", value="User 1")
player_name_2 = st.sidebar.text_input("Player 2 Name", value="User 2")

if st.sidebar.button("Create Championship") and championship_name:
    st.session_state['championships'].append({
        'name': championship_name,
        'matches': []
    })
    # Write to Google Sheets
    sheet.append_row([championship_name, "", "", ""])  # Add new championship
    st.sidebar.success(f"Championship '{championship_name}' created!")

# Selecting a Championship
if st.session_state['championships']:
    st.sidebar.header("Select Championship")
    selected_championship = st.sidebar.selectbox("Select Championship", [c['name'] for c in st.session_state['championships']])
    championship = next(c for c in st.session_state['championships'] if c['name'] == selected_championship)
    
    # Logging a new match result
    st.sidebar.header("Log Match Result")
    winner = st.sidebar.selectbox("Winner", [player_name_1, player_name_2, "User 3"])
    colour = st.sidebar.selectbox("Winner's Colour", ["White", "Black"])
    match_date = st.sidebar.date_input("Match Date", value=datetime.date.today())  # Default to today
    if st.sidebar.button("Save Match Result"):
        championship['matches'].append({
            'winner': winner,
            'colour': colour,
            'date': match_date
        })
        # Also append to Google Sheet (with date)
        sheet.append_row([selected_championship, winner, colour, str(match_date)])
        st.sidebar.success(f"Match result saved for championship '{selected_championship}'!")

    # Displaying Championship Overview
    st.write(f"### Championship: {selected_championship}")
    if championship['matches']:
        match_data = pd.DataFrame(championship['matches'])
        st.write("### Match Results:")
        st.write(match_data)

    # Displaying Overall Statistics for Selected Championship
    if st.checkbox("Show Overall Statistics for Selected Championship"):
        player_wins = match_data['winner'].value_counts()
        st.write("### Overall Statistics for Selected Championship:")
        for player, wins in player_wins.items():
            st.write(f"{player} Wins: {wins}")

    # Displaying Overall Statistics Across All Championships
    if st.checkbox("Show Overall Statistics Across All Championships"):
        all_matches = []
        for champ in st.session_state['championships']:
            all_matches.extend(champ['matches'])
        if all_matches:
            all_matches_data = pd.DataFrame(all_matches)
            overall_wins = all_matches_data['winner'].value_counts()
            st.write("### Overall Statistics Across All Championships:")
            for player, wins in overall_wins.items():
                st.write(f"{player} Wins: {wins}")

else:
    st.write("No championships available. Please create a new championship to get started.")

# Footer
st.write("""
---
Developed by FlyBoat
""")
