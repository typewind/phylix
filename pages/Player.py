import streamlit as st
import pandas as pd
import altair as alt
from pre_processing import df

# process data
RTP_THRESHOLD = 0.9
IMBALANCE = 0.1
ACWR_LOWER = 0.8
ACWR_UPPER = 1.3

st.set_page_config(layout="wide")

st.markdown("# Player Performance Monitor")
st.sidebar.markdown("# Player")

# Team filter
teams = df['Team Name'].unique()
default_team = 'Team1' if 'Team1' in teams else teams[0]
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Filter the DataFrame by selected teams to get the list of players
filtered_team_df = df[df['Team Name'].isin(selected_teams)]

# Player filter (single drop down)
players = filtered_team_df['Player'].unique()
default_player = players[0] if len(players) > 0 else ''
selected_player = st.sidebar.selectbox('Player', players, index=0 if default_player else -1)

# Season filter
seasons = df['Season'].unique()
default_seasons = ['2021/22', '2022/23'] if '2021/22' in seasons and '2022/23' in seasons else seasons
selected_seasons = st.sidebar.multiselect('Season', seasons, default_seasons)


# Date filter
date_min = df['Date'].min().date()
date_max = df['Date'].max().date()
selected_dates = st.sidebar.slider('Date', min_value=date_min, max_value=date_max, value=(date_min, date_max))


# Filter the data based on selections
filtered_df = df[
    (df['Team Name'].isin(selected_teams)) &
    (df['Season'].isin(selected_seasons)) &
    (df['Player'] == selected_player) &
    (df['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df['Date'] <= pd.to_datetime(selected_dates[1]))
]

print(filtered_df.head())