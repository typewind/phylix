import streamlit as st
import pandas as pd
import altair as alt
from tools import info_box, metrics_classes, team_individual_graph, submit_team_comment

df_all = pd.read_csv("./data/df_all.csv", parse_dates=["Date"], date_format='%Y-%m-%d')
st.set_page_config(layout="wide")
comment_table = pd.read_csv("./data/team_daily_training_comment.csv")

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

attendance = len(filtered_df)
if attendance:
    year_week = filtered_df["Year-Week"].values[0]
else:
    year_week = "No session"

filtered_df_week = df_all[
    (df_all['Team Name'] == selected_teams) &
    (df_all["Year-Week"] == year_week)
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
    title=f"Training Periodization"
)

# Display the bar chart in the sidebar below the date selector
st.sidebar.altair_chart(bar_chart, use_container_width=True)

st.markdown(f"# {selected_date}({year_week}) {selected_teams} Training Overview")

# traffic light
attendance_num, avg_duration, avg_distance, avg_load, avg_intensity, avg_sprint = st.columns(6)
with attendance_num:
    st.markdown(info_box(sline="Attendance",
                        iconname = "fas fa-users",
                        color_box = (39, 158, 255),
                        i=attendance if attendance else year_week
                        ),
            unsafe_allow_html=True)
with avg_duration:
    if attendance:
        today = filtered_df["Duration"].mean().round(1)
        max_of_avg_of_weekday= filtered_df_week.groupby("Weekday")["Duration"].mean().max()
        percentage = ((today/max_of_avg_of_weekday)*100).round(0)
    else:
        today = year_week
        percentage = 100
    st.markdown(info_box(sline="Avg Duration",
                        iconname = "fa fa-clock",
                        color_box =(0, 231, 255),
                        i=f"""{today}""",
                        percentage=percentage
                        ),
            unsafe_allow_html=True)
    

with avg_distance:
    if attendance:
        today = filtered_df["Total Distance(m)"].mean().round(1)
        max_of_avg_of_weekday= filtered_df_week.groupby("Weekday")["Total Distance(m)"].mean().max()
        percentage = ((today/max_of_avg_of_weekday)*100).round(0)
    else:
        today = year_week
        percentage = 100
    st.markdown(info_box(sline="Avg Distance",
                        iconname = "fa fa-clock",
                        color_box =(0, 231, 255),
                        i=f"""{today}""",
                        percentage=percentage
                        ),
                unsafe_allow_html=True)
with avg_load:
    if attendance:
        today = filtered_df["Total Player Load"].mean().round(1)
        max_of_avg_of_weekday= filtered_df_week.groupby("Weekday")["Total Player Load"].mean().max()
        percentage = ((today/max_of_avg_of_weekday)*100).round(0)
    else:
        today = year_week
        percentage = 100
    st.markdown(info_box(sline="Avg Load",
                        iconname = "fa fa-clock",
                        color_box =(0, 231, 255),
                        i=f"""{today}""",
                        percentage=percentage
                        ),
                unsafe_allow_html=True)
with avg_intensity:
    today = filtered_df["High Intensity Distance(m)"].mean().round(1)
    max_of_avg_of_weekday= filtered_df_week.groupby("Weekday")["High Intensity Distance(m)"].mean().max()
    percentage = ((today/max_of_avg_of_weekday)*100).round(1)
    st.markdown(info_box(sline="Avg High Intensity(m)",
                        iconname = "fa fa-clock",
                        color_box =(0, 231, 255),
                        i=f"""{today}""" if attendance else year_week,
                        percentage=percentage
                        ),
                unsafe_allow_html=True)
with avg_sprint:
    today = filtered_df["Sprint Distance(m)"].mean().round(1)
    max_of_avg_of_weekday= filtered_df_week.groupby("Weekday")["Sprint Distance(m)"].mean().max()
    percentage = ((today/max_of_avg_of_weekday)*100).round(0)
    st.markdown(info_box(sline="Avg Sprint",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=f"""{today}""" if attendance else year_week,
                        percentage=percentage
                         ),
                unsafe_allow_html=True)
                
st.markdown("---")
# Create a Streamlit container
with st.container():
    volumn, intensity = st.columns(2)
    agility, ima = st.columns(2)
    with volumn:
        st.markdown(f"### Volumn")
        selected_volumn = st.selectbox(f"Select Volumn Metric", metrics_classes["Volumn"], key="Volumn")
        st.altair_chart(team_individual_graph(filtered_df, filtered_df_week, selected_volumn), use_container_width=True, theme="streamlit")
    with intensity:
        st.markdown(f"### Intesity")
        selected_intensity = st.selectbox(f"Select intensity Metric", metrics_classes["Intensity"], key="intensity")
        st.altair_chart(team_individual_graph(filtered_df, filtered_df_week, selected_intensity), use_container_width=True, theme="streamlit")
    with agility:
        st.markdown(f"### Agility")
        selected_agility = st.selectbox(f"Select Agility Metric", metrics_classes["Agility"] + ["Maximum Velocity(m/s)"], key="Agility")
        st.altair_chart(team_individual_graph(filtered_df, filtered_df_week, selected_agility), use_container_width=True, theme="streamlit")
    with ima:
        st.markdown(f"### IMA")
        selected_ima = st.selectbox(f"Select IMA Metric", metrics_classes["IMA"], key="IMA")
        st.altair_chart(team_individual_graph(filtered_df, filtered_df_week, selected_ima), use_container_width=True, theme="streamlit")


# Comment area
with st.container():
    st.markdown("**Comment:**")
    team_comment = comment_table[(comment_table["Team"] == selected_teams)]

    comment_list = (team_comment["User"] + ": " + team_comment["Comment"]).values
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
        submit_team_comment(selected_teams, selected_date, 
                       comment, user, comment_table, "./data/team_daily_training_comment.csv")
        # reset comments
        comment = ""
        user = ""
        st.rerun()