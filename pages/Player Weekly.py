import streamlit as st
import pandas as pd
import altair as alt
from tools import info_box, draw_acwr, metrics_classes, get_not_passed_metrics, submit_comment

df_all = pd.read_csv("./data/df_all.csv", parse_dates=["Date"], date_format='%Y-%m-%d')
df_week_player = pd.read_csv("./data/df_week_player.csv", parse_dates=["Date"], date_format='%Y-%m-%d')
comment_table = pd.read_csv("./data/player_weekly_review_comment.csv")


# ========================
# The Player Page
# ========================

st.set_page_config(layout="wide")

st.markdown("# Player Weekly Performance Monitor")
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

# Filter for the traffic light
filtered_team_traffic_df = df_all[(df_all['Team Name'].isin(selected_teams)) &     
                                  (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
                                  (df_all['Date'] <= pd.to_datetime(selected_dates[1]))]

filtered_team_traffic_df_week = df_week_player[(df_week_player['Team Name'].isin(selected_teams)) &     
                                  (df_week_player['Date'] >= pd.to_datetime(selected_dates[0])) &
                                  (df_week_player['Date'] <= pd.to_datetime(selected_dates[1]))]



# Filter the data based on selections
filtered_df_all_player = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_week_player = df_week_player[
    (df_week_player['Team Name'].isin(selected_teams)) &
    (df_week_player['Season'].isin(selected_seasons)) &
    (df_week_player['Player'] == selected_player) &
    (df_week_player['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_week_player['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_week_team = df_week_player[
    (df_week_player['Team Name'].isin(selected_teams)) &
    (df_week_player['Season'].isin(selected_seasons)) &
    (df_week_player['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_week_player['Date'] <= pd.to_datetime(selected_dates[1]))
]



# ========================
# Info Box
# ========================
total_players, intensity_risk, agi_risk, ima_risk, vol_risk, imba= st.columns(6)
with total_players:
    st.markdown(info_box(sline="Total Players Selected",
                        iconname = "fas fa-users",
                        color_box = (39, 158, 255),
                        i=len(filtered_team_traffic_df_week['Player'].unique())
                        ),
            unsafe_allow_html=True)
with vol_risk:
    st.markdown(info_box(sline="Volumn Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_team_traffic_df_week[filtered_team_traffic_df_week["Volumn Risk Score"]!=0]["Player"].dropna().unique())),
                unsafe_allow_html=True)
with intensity_risk:
    st.markdown(info_box(sline="Intensity Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_team_traffic_df_week[filtered_team_traffic_df_week["Intensity Risk Score"]!=0]["Player"].dropna().unique())),
                unsafe_allow_html=True)
with agi_risk:
    st.markdown(info_box(sline="Agility Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_team_traffic_df_week[filtered_team_traffic_df_week["Agility Risk Score"]!=0]["Player"].dropna().unique())),
                unsafe_allow_html=True)
with ima_risk:
    st.markdown(info_box(sline="IMA Risk",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(0, 231, 255),
                         i=len(filtered_team_traffic_df_week[filtered_team_traffic_df_week["IMA Risk Score"]!=0]["Player"].dropna().unique())),
                unsafe_allow_html=True)
with imba:
    st.markdown(info_box(sline="Imbalance",
                         iconname = "fas fa-balance-scale-right",
                         color_box=(0, 255, 246),
                         i=len(filtered_team_traffic_df_week[filtered_team_traffic_df_week["Is IMA Imbalance"]]["Player"].dropna().unique())),
                unsafe_allow_html=True)
                
st.markdown("---")

def metrics_dropdown(metrics):
    pass

with st.container():
    player, team = st.columns(2)
    with team:
        volumn_chart, intensity_chart = st.columns(2)
        agility_chart, ima_chart = st.columns(2)
        with volumn_chart:
            selected_metric_volumn = st.selectbox("Select Volumn Metric", metrics_classes["Volumn"])
            st.altair_chart(draw_acwr(filtered_df_week_player, selected_metric_volumn),use_container_width=True, theme="streamlit")
        with intensity_chart:
            selected_metric_intensity = st.selectbox("Select Intensity Metric", metrics_classes["Intensity"])
            st.altair_chart(draw_acwr(filtered_df_week_player, selected_metric_intensity), use_container_width=True, theme="streamlit")
        with agility_chart:
            selected_metric_agility = st.selectbox("Select Agility Metric", metrics_classes["Agility"])
            st.altair_chart(draw_acwr(filtered_df_week_player, selected_metric_agility), use_container_width=True, theme="streamlit")
        with ima_chart:
            selected_metric_ima = st.selectbox("Select IMA Metric", metrics_classes['IMA'])
            st.altair_chart(draw_acwr(filtered_df_week_player, selected_metric_ima),use_container_width=True, theme="streamlit")


    with player: 
        st.subheader(f"**{selected_player} Report**")
        not_pass_metrics = get_not_passed_metrics(filtered_df_week_player, metrics_classes)
        # Description
        st.markdown(f"""During {selected_dates[0]} and {selected_dates[1]},
                   {selected_player}, the {filtered_df_week_player["Position"].values[-1]} of 
                    {", ".join(str(x) for x in filtered_df_week_player["Team Name"].unique())}:""")
        # check if any metrics abnormal
        for key, value in metrics_classes.items():
            if key not in not_pass_metrics :
                st.markdown(f"{key} - performance are normal.")
            else:
                st.markdown(f"""- **{key}**: Warning on <span style="color:#FF4B4B;">  {", ".join(str(x) for x in not_pass_metrics[key])} </span>.""", unsafe_allow_html=True)
        # check if imbalance
        if any(filtered_df_week_player["Is IMA Imbalance"]):
            st.markdown(f"""- The result of <span style="color:#FF4B4B;"> IMA COD </span> shows risks. """, unsafe_allow_html=True)
        else:
            st.markdown("- The IMA CODs are balanced.")

        # Comment area
        st.markdown("**Comment:**")
        comment_list = comment_table[(comment_table["Player ID"] == selected_player)]["Comment"].values
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
        comment = st.text_input('Add Comment:', '')
        if st.button('Submit'):
            submit_comment(selected_player, comment, comment_table)
            # reset comments
            comment = ""
            st.rerun()