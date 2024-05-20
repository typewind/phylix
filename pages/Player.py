import streamlit as st
import pandas as pd
import altair as alt
from pre_processing import df_all, df_week_player, df_week_team, info_box


# ========================
# The Player Page
# ========================

st.set_page_config(layout="wide")

st.markdown("# Player Performance Monitor")
st.sidebar.markdown("# Player")

# ========================
# Filter
# ========================
teams = df_all['Team Name'].unique()
default_team = 'Team1' if 'Team1' in teams else teams[0]
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Filter the DataFrame by selected teams to get the list of players
filtered_team_df = df_all[df_all['Team Name'].isin(selected_teams)]

# Player filter (single drop down)
players = filtered_team_df['Player'].unique()
default_player = players[0] if len(players) > 0 else ''
selected_player = st.sidebar.selectbox('Player', players, index=0 if default_player else -1)

# Season filter
seasons = df_all['Season'].unique()
default_seasons = ['2021/22', '2022/23'] if '2021/22' in seasons and '2022/23' in seasons else seasons
selected_seasons = st.sidebar.multiselect('Season', seasons, default_seasons)


# Date filter
date_min = df_all['Date'].min().date()
date_max = df_all['Date'].max().date()
selected_dates = st.sidebar.slider('Date', min_value=date_min, max_value=date_max, value=(date_min, date_max))


# Filter the data based on selections
filtered_df_all_player = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_week_player = df_week_player[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_week_team = df_week_player[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

# filtered_df_team_player = df_week_team[
#     (df_all['Team Name'].isin(selected_teams)) &
#     (df_all['Season'].isin(selected_seasons)) &
#     (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
#     (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
# ]


# ========================
# Info Box
# ========================
total_players, intensity_risk, agi_risk, ima_risk, vol_risk, imba= st.columns(6)
with total_players:
    st.markdown(info_box(sline="Total Players Selected",
                        iconname = "fas fa-users",
                        color_box = (39, 158, 255),
                        i=len(filtered_df_week_team["Player"].unique())
                        ),
            unsafe_allow_html=True)
with vol_risk:
    st.markdown(info_box(sline="Volumn Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_df_week_team[filtered_df_week_team["Volumn Risk Score"]!=0]["Player"].unique())),
                unsafe_allow_html=True)
with intensity_risk:
    st.markdown(info_box(sline="Intensity Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_df_week_team[filtered_df_week_team["Intensity Risk Score"]!=0]["Player"].unique())),
                unsafe_allow_html=True)
with agi_risk:
    st.markdown(info_box(sline="Agility Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_df_week_team[filtered_df_week_team["Agility Risk Score"]!=0]["Player"].unique())),
                unsafe_allow_html=True)
with ima_risk:
    st.markdown(info_box(sline="IMA Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_df_week_team[filtered_df_week_team["IMA Risk Score"]!=0]["Player"].unique())),
                unsafe_allow_html=True)
with imba:
    st.markdown(info_box(sline="Imbalance",
                         iconname = "fas fa-balance-scale-right",
                         color_box=(0, 255, 246),
                         i=len(filtered_df_week_team[filtered_df_week_team["Is IMA Imbalance"]]["Player"].unique())),
                unsafe_allow_html=True)
                
st.markdown("---")

