import streamlit as st
import pandas as pd
import altair as alt
from tools import info_box, draw_acwr, metrics_classes, get_not_passed_metrics, submit_comment, draw_ima_cod

df_all = pd.read_csv("./data/df_all.csv", parse_dates=["Date"], date_format='%Y-%m-%d')
comment_table = pd.read_csv("./data/player_daily_review_comment.csv")


# ========================
# The Player Page
# ========================

st.set_page_config(layout="wide")


# ========================
# Filter
# ========================
teams = df_all['Team Name'].unique()
default_team = 'Team1' if 'Team1' in teams else teams[0]
selected_teams = st.sidebar.selectbox('Team', teams)

# Date filter
date_min = df_all.dropna()['Date'].min().date()
date_max = df_all.dropna()['Date'].max().date()
selected_date = st.sidebar.date_input('Date', value=date_max, min_value=date_min, max_value=date_max, format="YYYY/MM/DD")
selected_weekday = pd.to_datetime(selected_date).strftime('%A')

# filtered df
filtered_df = df_all[
    (df_all['Team Name']==selected_teams) &
    (df_all['Date'] == pd.to_datetime(selected_date))
].dropna()

# Player filter
players = filtered_df['Player'].unique()
default_player = players[0] if len(players) > 0 else ''
selected_player = st.sidebar.selectbox('Player', players, index=0 if default_player else -1)

attendance = len(filtered_df)
if attendance:
    year_week = filtered_df["Year-Week"].values[0]
else:
    year_week = "No session"

filtered_df_week = df_all[
    (df_all['Team Name'] == selected_teams) &
    (df_all["Year-Week"] == year_week) &
    (df_all["Player"] == selected_player)
].dropna()

# team daily status
avg_cols = [ "Total Distance(m)", "Total Player Load","Duration", "High Intensity Distance(m)", "Sprint Distance(m)"]
selected_team_metric = st.sidebar.selectbox('Weekly Team Overview', avg_cols)
mean_by_weekday = filtered_df_week.groupby('Weekday')[selected_team_metric].mean().reset_index()
# Create the bar chart with Altair
highlight = alt.condition(
    alt.datum.Weekday == selected_weekday,
    alt.value('orange'),  # Highlight color
    alt.value('steelblue')  # Default color
)

bar_chart = alt.Chart(mean_by_weekday).mark_bar().encode(
    x=alt.X('Weekday', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
    y=alt.Y(f'{selected_team_metric}:Q', title=f'Avg {selected_team_metric}'),
    color=highlight
).properties(
    title=f"{year_week} Training Periodization"
)

# Display the bar chart in the sidebar below the date selector
st.sidebar.altair_chart(bar_chart, use_container_width=True)


# Filter the data based on selections
filtered_df_player = df_all[
    (df_all['Team Name']== selected_teams) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] == pd.to_datetime(selected_date))
]

filtered_df_player_all = df_all[
    (df_all['Team Name']== selected_teams) &
    (df_all['Player'] == selected_player) 
]

# team df: filtered_df

st.markdown(f"# {selected_player}: {selected_date} Report")
# ========================
# Info Box
# ========================
total_distance, sprint, high_intensity_dist, max_velocity, duration = st.columns(5)
with total_distance:
    if len(filtered_df_player):
        value = filtered_df_player["Total Distance(m)"].round(1).values[0]
        week_max = filtered_df_week["Total Distance(m)"].round(1).max()
        pctg = (value/week_max) * 100
    else:
        value = "No Session"
        pctg = 100
    st.markdown(info_box(sline="Total Distance(m)",
                        iconname = "fas fa-users",
                        color_box = (0, 231, 255),
                        i=value,
                        percentage=pctg
                        ),
            unsafe_allow_html=True)
with sprint:
    if len(filtered_df_player):
        value = filtered_df_player["Sprint Distance(m)"].round(1).values[0]
        week_max = filtered_df_week["Sprint Distance(m)"].round(1).max()
        pctg = (value/week_max) * 100
    else:
        value = "No Session"
        pctg = 100
    st.markdown(info_box(sline="Sprint(m)",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=value,
                         percentage=pctg
                         ),
                unsafe_allow_html=True)
with high_intensity_dist:
    if len(filtered_df_player):
        value = filtered_df_player["High Intensity Distance(m)"].round(1).values[0]
        week_max = filtered_df_week["High Intensity Distance(m)"].round(1).max()
        pctg = (value/week_max) * 100
    else:
        value = "No Session"
        pctg = 100
    st.markdown(info_box(sline="High Intensity(m)",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=value,
                         percentage=pctg
                         ),
                unsafe_allow_html=True)
with max_velocity:
    if len(filtered_df_player):
        value = filtered_df_player["Maximum Velocity(m/s)"].round(1).values[0]
        week_max = filtered_df_week["Maximum Velocity(m/s)"].round(1).max()
        pctg = (value/week_max) * 100
    else:
        value = "No Session"
        pctg = 100
    st.markdown(info_box(sline="Max Velocity(m/s)",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=value,
                         percentage=pctg
                         ),
                unsafe_allow_html=True)
with duration:
    if len(filtered_df_player):
        value = filtered_df_player["Duration"].round(1).values[0]
        week_max = filtered_df_week["Duration"].round(1).max()
        pctg = (value/week_max) * 100
        print(value, week_max, pctg)
    else:
        value = "No Session"
        pctg = 100
    st.markdown(info_box(sline="Duration",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=value,
                         percentage=pctg
                         ),
                unsafe_allow_html=True)
                
st.markdown("---")

