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

st.markdown("# Player Daily Performance Monitor")
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

filtered_team_traffic_df_week = df_all[(df_all['Team Name'].isin(selected_teams)) &     
                                  (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
                                  (df_all['Date'] <= pd.to_datetime(selected_dates[1]))]



# Filter the data based on selections
filtered_df_all_player = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_all = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Player'] == selected_player) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]

filtered_df_week_team = df_all[
    (df_all['Team Name'].isin(selected_teams)) &
    (df_all['Season'].isin(selected_seasons)) &
    (df_all['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df_all['Date'] <= pd.to_datetime(selected_dates[1]))
]



# ========================
# Info Box
# ========================
total_players, intensity_risk, agi_risk, ima_risk, vol_risk, imba= st.columns(6)
with total_players:
    st.markdown(info_box(sline="Players Selected",
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


with st.container():
    player, info = st.columns(2)
    with player: 
        st.markdown(f"## {selected_player} Report")
        not_pass_metrics = get_not_passed_metrics(filtered_df_all, metrics_classes)
        # Description
        st.markdown(f"""During {selected_dates[0]} and {selected_dates[1]},
                   {selected_player}, the {filtered_df_all["Position"].values[-1]} of 
                    {", ".join(str(x) for x in filtered_df_all["Team Name"].unique())}:""")
        # check if any metrics abnormal
    with info:
        pass

for key, value in not_pass_metrics.items():
    with st.container():
        summary, visual = st.columns(2)
        with summary:
            st.markdown(f"### {key}")
            if key == "IMA":
                if any(filtered_df_all["Is IMA Imbalance"]):
                    st.markdown(f"""- The balance of <span style="color:#FF4B4B;"> IMA COD </span> shows risks. """, unsafe_allow_html=True)
                else:
                    st.markdown("- The IMA CODs are balanced.")
            else:
                if len(value)==0 :
                    st.markdown(f"- **{key}** - performance are normal.")
                else:
                    # Generate the bullet list with colored items
                    bullet_list = "\n".join([f'<li><span style="color:#FF4B4B;"> - {str(x)} </span></li>' for x in not_pass_metrics[key]])
                    st.markdown(f"""**Warning** on:\n<ul>{bullet_list}</ul>""", unsafe_allow_html=True)
        
        with visual:
            if key == "IMA":
                st.altair_chart(draw_ima_cod(filtered_df_all),use_container_width=True, theme="streamlit")
            else:
                selected_metric_volumn = st.selectbox(f"Select {key} Metric", metrics_classes[key])
                st.altair_chart(draw_acwr(filtered_df_all, selected_metric_volumn),use_container_width=True, theme="streamlit")


# Comment area
with st.container():
    st.markdown("**Comment:**")
    player_comment = comment_table[(comment_table["Player"] == selected_player)]
    comment_list = (player_comment["User"] + ": " + player_comment["Comment"]).values
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
        submit_comment(selected_player, comment, user, comment_table)
        # reset comments
        comment = ""
        user = ""
        st.rerun()
