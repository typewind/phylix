import streamlit as st
import pandas as pd
import altair as alt
import datetime
import time
from tools import create_sankey

# Set the page configuration to wide layout
st.set_page_config(layout="wide")
comment_table = pd.read_csv("./data/club_overview_comment.csv")

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
        "Total Distance(m)": 'mean',
        "Total Player Load": 'mean',
        "High Intensity Distance(m)": 'max',
        "Sprint Distance(m)": 'max',
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

agg_df = load_data('./data/df_all.csv')
df_all = pd.read_csv('./data/df_all.csv', parse_dates=["Date"], date_format='%Y-%m-%d')


st.sidebar.markdown("# Overview")


# Team filter
teams = agg_df['Team Name'].unique()
default_team = teams
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Date filter
date_min = df_all['Date'].min().date()
date_max = df_all['Date'].max().date()
selected_dates = st.sidebar.slider('Date', min_value=date_min, max_value=date_max, value=(date_min, date_max))

# Position filter
selected_position = st.sidebar.multiselect('Position', df_all["Position"].unique(), df_all["Position"].unique())


# Filter the data based on selections
filtered_df = agg_df[
    (agg_df['Team Name'].isin(selected_teams)) &
    (agg_df['Date'] >= pd.to_datetime(selected_dates[0])) &
    (agg_df['Date'] <= pd.to_datetime(selected_dates[1]))].dropna()

filtered_all = df_all[(df_all['Team Name'].isin(selected_teams)) &
                      (df_all['Position'].isin(selected_position)) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))].dropna()

st.markdown(f"# Club Performance Overview ({selected_dates[0]} to {selected_dates[1]})")
overall_cols = ["Attendance", "Total Distance(m)", "Total Player Load","Duration", 
                "High Intensity Distance(m)", "Sprint Distance(m)"]
rank_cols = ["Maximum Velocity(m/s)",  "High Intensity Distance(m)", "Sprint Distance(m)", 
             "Total Distance(m)", "Total Player Load", "Load Per Minute", 
             "Distance Per Minute", "Acc-Dec-COD Per Minute"]

rank, overview = st.columns(2)

# Create the Gantt chart per duration
with rank:
    selected_metric = st.selectbox('Session Metric', rank_cols)
    rank_df = filtered_all[["Player", "Team Name", "Position", "Date", selected_metric]].sort_values("Date").round(2).dropna()
    last_30_days_start = rank_df['Date'].max() - datetime.timedelta(days=30)
    last_30_days_df = rank_df[(rank_df['Date'] >= last_30_days_start) &
                              (rank_df['Date'] >= pd.to_datetime(selected_dates[0])) 
                              ]
    last_30_days_array = last_30_days_df.groupby('Player').apply(lambda x: list(x[selected_metric])).reset_index(name='Last 30 Days')
    rank_df = rank_df.merge(last_30_days_array, on='Player', how='left')

    st.write(f'## {selected_metric} Leaderboard')
    st.dataframe(rank_df.sort_values(selected_metric, ascending=False).head(10), 
                 hide_index=True,
                 use_container_width = True,
                 column_config = { "Date": st.column_config.DateColumn(format = 'Y-MM-DD'),
                                  "Last 30 Days": st.column_config.LineChartColumn(f"Last 30 Days of {selected_dates[1]}", y_min=0, y_max=11),
                     }
                 )
    # Group by Position and calculate the average of selected metrics
    st.write(f'## Avg {selected_metric} by Position')
    avg_metric_by_position = filtered_all.groupby('Position')[selected_metric].mean().reset_index().round(2)

    bars = alt.Chart(avg_metric_by_position).mark_bar().encode(
        x=alt.X('Position:N', title='Position', sort='-y'),
        y=alt.Y(f'{selected_metric}:Q', title=f'Avg {selected_metric}'),
        tooltip=['Position:N', f'{selected_metric}:Q']
    )
    # Add text labels to the bars
    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Adjust vertical alignment of the text
    ).encode(
        text=alt.Text(f'{selected_metric}:Q', format='.2f')
    )
    bar_chart = (bars + text).properties(
    title=f'Average {selected_metric} by Position'
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # Group by team and calculate the average of selected metrics
    st.write(f'## Avg {selected_metric} by Team')
    avg_metric_by_position = filtered_all.groupby('Team Name')[selected_metric].mean().reset_index().round(2)

    bars = alt.Chart(avg_metric_by_position).mark_bar().encode(
        x=alt.X('Team Name:N', title='Team', sort='-y'),
        y=alt.Y(f'{selected_metric}:Q', title=f'Avg {selected_metric}'),
        tooltip=['Team Name:N', f'{selected_metric}:Q']
    )
    # Add text labels to the bars
    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Adjust vertical alignment of the text
    ).encode(
        text=alt.Text(f'{selected_metric}:Q', format='.2f')
    )
    bar_chart = (bars + text).properties(
    title=f'Average {selected_metric} by Team'
    )
    st.altair_chart(bar_chart, use_container_width=True)

with overview:
    selected_metric = st.selectbox('Session Metric', overall_cols)
    st.write(f'## Weekly {selected_metric} Per Team')
    gantt_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelFontSize=16, titleFontSize=20)),
        y=alt.Y('Team Name:N', title='Team', axis=alt.Axis(labelFontSize=16, titleFontSize=20)),
        color=alt.Color(f'{selected_metric}:Q', title=f'{selected_metric}', scale=alt.Scale(scheme='turbo')),
        tooltip=['Date:T', 'Team Name:N', f'{selected_metric}:Q']
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(gantt_chart, use_container_width=True)    
    # Create Sankey diagrams for each date range using 'Team Name'
    # Specify node positions for specific teams (Team2 and Team4 in this example)
    node_positions = {
        'Team1': (None, None),
        'Team2': (None, None),  
        'Team3': (0, 0),
        'Team4': (None, None),
        'Team5': (None, None),
        'Team6': (None, None),
        'Team7': (0.95, 0.8),
        'Team8': (0.7, 0.9),
    }
    fig = create_sankey(filtered_all, selected_dates, 'Team Name', node_positions)
    st.markdown(f"## Player Movements Between Teams ({ selected_dates[0]} to {selected_dates[1]})")
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")



with st.container():
    st.markdown("**Comment:**")
    comment_list = (comment_table["User"] + ": " + comment_table["Comment"]).values
    if len(comment_list)==0:
        st.markdown("Ask performance team for further advice.")
    else:
        for x in comment_list:
            st.markdown(f"- {x}")

    st.markdown('''
                <style>
                [data-testid="stMarkdownContainer"] ul{
                    padding-left:40px;
                }
                </style>
                ''', unsafe_allow_html=True)

    # add comment
    user = st.text_input('Your Name', '')
    comment = st.text_area('Comment:', '')
    if st.button('Submit'):

        ts = time.time()
        now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        new_row = pd.DataFrame({'Timestamp': [now],'User':user, 'Comment': [comment]})
        comment_table = pd.concat([comment_table, new_row], ignore_index=True)
        comment_table.to_csv("./data/club_overview_comment.csv", encoding='utf-8', index=False)
        # reset comments
        comment = ""
        user = ""
        st.rerun()
st.markdown("""
    How We Aggregate Player Metrics:
    - Attendance: The average player has attended the session.
    - Duration: The average time players spend.
    - Total Distance (m): The average distance players cover.
    - Total Player Load: The average workload on players.
    - High Intensity Distance (m): The peak distance at high intensity.
    - Sprint Distance (m): The longest sprint distance.
""")