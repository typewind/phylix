import streamlit as st
import pandas as pd
import altair as alt

from pre_processing import info_box


st.set_page_config(layout="wide")
# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('./data/data_cleaned.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Year'] = df['Date'].dt.year
    return df

df = load_data()

# Sidebar filters
st.sidebar.header('Filters')

# Year filter
years = df['Year'].unique()
selected_years = st.sidebar.multiselect('Year', years, years)

# Week filter
weeks = df['Week'].unique()
selected_weeks = st.sidebar.multiselect('Week', weeks, weeks)

# Filter the data based on selections
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Week'].isin(selected_weeks))
]

# Calculate average training duration per player per week
avg_duration_df = filtered_df.groupby(['Player', 'Year', 'Week']).agg({
    'Duration': 'mean'
}).reset_index()

# Create a new 'Date' column representing the first day of the week
avg_duration_df['Date'] = pd.to_datetime(avg_duration_df['Year'].astype(str) + avg_duration_df['Week'].astype(str) + '1', format='%G%V%u') + pd.offsets.Week(weekday=0)


# Timeline chart to show player movement between teams
st.write('## Player Movement Between Teams Over Time')

# Calculate player movements
movement_df = df[['Player', 'Team Name', 'Date']].drop_duplicates().sort_values(['Player', 'Date'])
movement_df['Prev Team'] = movement_df.groupby('Player')['Team Name'].shift(1)
movement_df = movement_df.dropna(subset=['Prev Team'])
movement_df = movement_df[movement_df['Team Name'] != movement_df['Prev Team']]

# Timeline chart using Altair
timeline_chart = alt.Chart(movement_df).mark_line(point=True).encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelFontSize=14, titleFontSize=16)),
    y=alt.Y('Player:N', title='Player', axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    color='Team Name:N',
    tooltip=['Date:T', 'Player:N', 'Prev Team:N', 'Team Name:N']
).properties(
    width=1000,
    height=600
).interactive()

st.altair_chart(timeline_chart, use_container_width=True)