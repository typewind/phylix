import streamlit as st
import pandas as pd
import altair as alt
from tools import info_box, metrics_classes, team_individual_graph

df_all = pd.read_csv("./data/df_all.csv", parse_dates=["Date"], date_format='%Y-%m-%d')
st.set_page_config(layout="wide")


st.sidebar.markdown("# Team")


teams = df_all['Team Name'].unique()
default_team = 'Team1' if 'Team1' in teams else teams[0]
selected_teams = st.sidebar.multiselect('Team', teams, default_team)

# Date filter
date_min = df_all.dropna()['Date'].min().date()
date_max = df_all.dropna()['Date'].max().date()
selected_date = st.sidebar.date_input('Date', value=date_max, min_value=date_min, max_value=date_max, format="YYYY/MM/DD")

# filtered df
filtered_df = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Date'] == pd.to_datetime(selected_date))
].dropna()

attendance = len(filtered_df)
if attendance:
    year_week = filtered_df["Year-Week"].values[0]
else:
    year_week = "No session"

filtered_df_week = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all["Year-Week"] == year_week)
].dropna()

# team daily status
avg_cols = ["Duration", "Total Distance(m)", "Total Player Load", "High Intensity Distance(m)", "Sprint Distance(m)"]


st.markdown(f"# {selected_date}({year_week}) Team Overview")

# traffic light
avg_duration, avg_distance, avg_load, avg_intensity, avg_sprint = st.columns(5)
with avg_duration:
    st.markdown(info_box(sline="Avg Duration",
                        iconname = "fas fa-users",
                        color_box = (39, 158, 255),
                        i=filtered_df["Duration"].mean().round(2) if attendance else year_week
                        ),
            unsafe_allow_html=True)
with avg_distance:
    st.markdown(info_box(sline="Avg Total Distance(m)",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=filtered_df["Total Distance(m)"].mean().round(2) if attendance else year_week
                         ),
                unsafe_allow_html=True)
with avg_load:
    st.markdown(info_box(sline="Avg Load",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=filtered_df["Total Player Load"].mean().round(2) if attendance else year_week
                         ),
                unsafe_allow_html=True)
with avg_intensity:
    st.markdown(info_box(sline="Avg High Speed Run(m)",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=filtered_df["High Intensity Distance(m)"].mean().round(2) if attendance else year_week
                         ),
                unsafe_allow_html=True)
with avg_sprint:
    st.markdown(info_box(sline="Avg Sprint",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=filtered_df["Sprint Distance(m)"].mean().round(2) if attendance else year_week
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


    # for i, (key, values) in enumerate(metrics_classes.items()):
    #     with columns[i]:
    #         st.markdown(f"### {key}")
    #         selected_metric = st.selectbox(f"Select {key} Metric", values, key=key)
    #         st.altair_chart(team_individual_graph(filtered_df, filtered_df_week, selected_metric), use_container_width=True, theme="streamlit")
