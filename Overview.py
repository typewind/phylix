import streamlit as st
import pandas as pd
import altair as alt

# Caching the data loading function to improve performance
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    attendance_df = df.dropna().groupby(['Team Name', 'Date'])['Player'].nunique().reset_index()
    attendance_df.rename(columns={'Player': 'Attendance'}, inplace=True)
    
    # Merge attendance back into the original DataFrame
    df = df.merge(attendance_df, on=['Team Name', 'Date'])
    return df

df = load_data('./data/data_cleaned.csv')

st.markdown("# Physical Performance Monitor")
st.sidebar.markdown("# Overview")

# Team filter
teams = df['Team Name'].unique()
default_team = 'Team1' if 'Team1' in teams else teams[0]
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Season filter
seasons = df['Season'].unique()
default_seasons = ['2021/22', '2022/23'] if '2021/22' in seasons and '2022/23' in seasons else seasons
selected_seasons = st.sidebar.multiselect('Season', seasons, default_seasons)

# Weekday filter
weekdays = df['Weekday'].unique()
default_weekdays = weekdays
selected_weekdays = st.sidebar.multiselect('Weekday', weekdays, default_weekdays)

# Date filter
date_min = df['Date'].min().date()
date_max = df['Date'].max().date()
selected_dates = st.sidebar.slider('Date', min_value=date_min, max_value=date_max, value=(date_min, date_max))

# Define metrics
metrics = ['Duration', 'Attendance']

# Filter the data based on selections
filtered_df = df[
    (df['Team Name'].isin(selected_teams)) &
    (df['Season'].isin(selected_seasons)) &
    (df['Weekday'].isin(selected_weekdays)) &
    (df['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df['Date'] <= pd.to_datetime(selected_dates[1]))
]
filtered_df['Date'] = pd.to_datetime(filtered_df['Year'].astype(str) + filtered_df['Week'].astype(str) + '1', format='%G%V%u') + pd.offsets.Week(weekday=0)

print(filtered_df.head())


# Create a selection interval for zooming and panning
zoom = alt.selection_interval(bind='scales')

# Plotting each metric
for metric in metrics:
    st.write(f'## {metric}')
    
    chart = alt.Chart(filtered_df).mark_line().encode(
        x='Date:T',
        y=f'{metric}:Q',
        color='Team Name:N'
    ).properties(
        width=1000,
        height=200
    ).add_selection(
        zoom
    )
    
    st.altair_chart(chart, use_container_width=True)