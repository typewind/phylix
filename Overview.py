import streamlit as st
import pandas as pd
import altair as alt

# Set the page configuration to wide layout
st.set_page_config(layout="wide")

# Caching the data loading function to improve performance
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    
    # Calculate attendance by counting the number of unique players per team per day
    attendance_df = df.dropna().groupby(['Team Name', 'Year', 'Week'])['Player'].nunique().reset_index()
    attendance_df.rename(columns={'Player': 'Attendance'}, inplace=True)
    
    # Calculate the average duration and median attendance per team per week
    agg_df = df.dropna().groupby(['Team Name', 'Year', 'Week']).agg({
        'Duration': 'mean',
        'Player': 'nunique'
    }).rename(columns={'Player': 'Attendance'}).reset_index()
    
    # Calculate average attendance for each team during the entire lifecycle
    avg_attendance = agg_df.groupby('Team Name')['Attendance'].mean().reset_index()
    avg_attendance.rename(columns={'Attendance': 'Avg Attendance'}, inplace=True)
    
    # Merge average attendance back into the aggregated DataFrame
    agg_df = agg_df.merge(avg_attendance, on='Team Name')
    
    # Filter based on the condition
    # agg_df['Duration'] = agg_df.apply(lambda row: 0 if row['Attendance'] < 0.25 * row['Avg Attendance'] else row['Duration'], axis=1)
    # agg_df['Attendance'] = agg_df.apply(lambda row: 0 if row['Attendance'] < 0.25 * row['Avg Attendance'] else row['Attendance'], axis=1)
    
    # Create a new 'Date' column representing the first day of the week
    agg_df['Date'] = pd.to_datetime(agg_df['Year'].astype(str) + agg_df['Week'].astype(str) + '1', format='%G%V%u') + pd.offsets.Week(weekday=0)
    
    return agg_df

agg_df = load_data('./data/data_cleaned.csv')

st.markdown("# Physical Performance Monitor")
st.sidebar.markdown("# Overview")

# Sidebar filters
st.sidebar.header('Filters')

# Team filter
teams = agg_df['Team Name'].unique()
default_team = teams
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Year filter
years = agg_df['Year'].unique()
selected_years = st.sidebar.multiselect('Year', years, years)

# Filter the data based on selections
filtered_df = agg_df[
    (agg_df['Team Name'].isin(selected_teams)) &
    (agg_df['Year'].isin(selected_years)) 
]

# Normalize attendance for alpha channel
min_attendance = filtered_df['Attendance'].min()
max_attendance = filtered_df['Attendance'].max()
filtered_df['Attendance_alpha'] = filtered_df['Attendance'].apply(lambda x: 0.01 + 0.95 * (x - min_attendance) / (max_attendance - min_attendance))


# Create the Gantt chart per duration
st.write('## Weekly Session Duration Per Team (2021/07/01 - 2023/06/30)')

gantt_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelFontSize=16, titleFontSize=20)),
    y=alt.Y('Team Name:N', title='Team', axis=alt.Axis(labelFontSize=16, titleFontSize=20)),
    color=alt.Color('Duration:Q', title='Avg Duration', scale=alt.Scale(scheme='turbo')),
    tooltip=['Date:T', 'Team Name:N', 'Duration:Q', 'Attendance:Q']
).properties(
    width=800,
    height=400
)
st.altair_chart(gantt_chart, use_container_width=True)

# Create the Gantt chart for attendance
st.write('## Weekly Session Attendance Per Team (2021/07/01 - 2023/06/30)')
attendance_gantt_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelFontSize=16, titleFontSize=20)),
    y=alt.Y('Team Name:N', title='Team', axis=alt.Axis(labelFontSize=16, titleFontSize=20)),
    color=alt.Color('Attendance:Q', title='Attendance', scale=alt.Scale(scheme='turbo')),
    tooltip=['Date:T', 'Team Name:N', 'Attendance:Q']
).properties(
    width=800,
    height=400
)

st.altair_chart(attendance_gantt_chart, use_container_width=True)

