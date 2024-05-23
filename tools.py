import altair as alt
import pandas as pd
import datetime
import time
import plotly.graph_objects as go


metrics_classes = {
    "Volumn": ['Total Distance(m)', 'Total Player Load', 'Duration'],
    "Intensity": ['Load Per Minute', 'Distance Per Minute', 'Acc-Dec-COD Per Minute'],
    "Agility": ['Acc 2m/s2 Total Effort','Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort', 'Dec 3m/s2 Total Effort'],
    "IMA": ['IMA COD(left)', 'IMA COD(right)'],
}




def info_box(color_box=(255, 75, 75), iconname="fas fa-balance-scale-right", sline="Observations", i=123):
    wch_colour_box = color_box
    wch_colour_font = (0, 0, 0)
    fontsize = 28
    valign = "left"
    iconname = iconname
    sline = sline
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    i = i

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                {wch_colour_box[1]}, 
                                                {wch_colour_box[2]}, 1); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}, 1); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-xs'></i> {i}
                            </style><BR><span style='font-size: 18px; 
                            margin-top: 0;'>{sline}</style></span></p>"""

    return lnk + htmlstr



def draw_acwr(plot_df, col):
    plot_df = plot_df.dropna()
    ewma_acwr = alt.Chart(plot_df).mark_line(point=alt.OverlayMarkDef(color="#FF7676"), color="#FA8072").encode(
    alt.X("Date"),
    alt.Y(f'{col} EWMA ACWR', axis=alt.Axis(title=f'{col} EWMA ACWR', titleColor='#FF7676')),
    alt.Tooltip(["Date:T", f"{col} EWMA ACWR", f"{col}:Q"])
    )

    # Create the dashed horizontal line at y = 1.5
    upper_ewma_acwr = alt.Chart(pd.DataFrame({'y': [1.5]})).mark_rule(strokeDash=[5, 5], color='#FF6969').encode(
        y='y:Q'
    )

    # Create the dashed horizontal line at y = 0.8
    lower_ewma_acwr = alt.Chart(pd.DataFrame({'y': [0.8]})).mark_rule(strokeDash=[5, 5], color='#FF6969').encode(
        y='y:Q'
    )
        
    chart = alt.Chart(plot_df).mark_bar(color="#0F52BA").encode(
        alt.X("Date:T", axis=alt.Axis(title="Date")),
        alt.Y(f"{col}:Q", axis=alt.Axis(title=f"{col}")),
        alt.Tooltip(["Date:T", f"{col}:Q", f"{col} EWMA ACWR"])
    )

    ewma_acwr_combined = alt.layer(
        ewma_acwr,
        upper_ewma_acwr,
        lower_ewma_acwr
    ).resolve_scale(
        y='shared'  # Share y-axis for the EWMA ACWR related charts
    )


    combined_chart = alt.layer(
        chart,
        ewma_acwr_combined
    ).resolve_scale(
        y='independent'  # Allow independent y-axes
    ).properties(
        title=f"{col} vs EWMA ACWR",
        width=600,
        height=300
    )

    return combined_chart


def get_not_passed_metrics(df, metrics_classes):
    not_pass_metrics = {}
    for key, value in metrics_classes.items():
        not_pass = [metric for metric in value if any(df[f"is_{metric}_abnormal"]!="Moderate")]
        not_pass_metrics[key] = not_pass
    return not_pass_metrics



def submit_comment(player_id,  text, user, comment_table):
    ts = time.time()
    now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame({'Player': [player_id], 'Timestamp': [now],'User':user, 'Comment': [text]})
    comment_table = pd.concat([comment_table, new_row], ignore_index=True)
    comment_table.to_csv("./data/player_weekly_review_comment.csv", encoding='utf-8', index=False)

def submit_team_comment(team, date, text, user, comment_table, path):
    ts = time.time()
    now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame({'Team': [team], 'Date': [date], 
                            'Timestamp': [now],'User':user, 'Comment': [text]})
    comment_table = pd.concat([comment_table, new_row], ignore_index=True)
    comment_table.to_csv(path, encoding='utf-8', index=False)



def draw_acc_dec():
    pass

def draw_ima_cod(player1):
    player1 = player1.dropna()

    # Melt the DataFrame to long format for Altair
    df_melted = player1.melt(id_vars=['Player', 'Date', 'IMA COD(Right) %', 'IMA COD(Left) %', 'IMA COD Imbalance'], 
                        value_vars=['IMA COD(left)', 'IMA COD(right)'], 
                        var_name='Type', 
                        value_name='Value').dropna()

    # Define colors
    colors = {'IMA COD(left)': '#0F52BA', 'IMA COD(right)': '#4A8CC7'}

    # Create the stack bar chart
    bar_chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('sum(Value):Q', axis=alt.Axis(title='IMA COD')),
        color=alt.Color('Type:N', scale=alt.Scale(domain=['IMA COD(left)', 'IMA COD(right)'], range=[colors['IMA COD(left)'], colors['IMA COD(right)']])),
        tooltip=[
            alt.Tooltip('Date:T', title='Date'),
            alt.Tooltip('IMA COD(Left) %:N', title='IMA COD(Left) %'),
            alt.Tooltip('IMA COD(Right) %:N', title='IMA COD(Right) %')
        ]
    ).properties(
        width=600,
        height=300
    )

    # Create the line chart for IMA COD Imbalance
    line_chart = alt.Chart(player1).mark_line(color='#FF7F3E').encode(
        x='Date:T',
        y=alt.Y('IMA COD Imbalance:Q', axis=alt.Axis(title='IMA COD Imbalance', titleColor='#FF7F3E')),
        tooltip=[
            alt.Tooltip('Date:T', title='Date'),
            alt.Tooltip('IMA COD Imbalance:Q', title='IMA COD Imbalance')
        ]
    )

    # Create the dashed horizontal line at y = 0.8
    balance_line = alt.Chart(pd.DataFrame({'y': [0.0]})).mark_rule(strokeDash=[5, 5], color='#FF7F3E').encode(
        y='y:Q'
    )

    balance_combined = alt.layer(
        line_chart,
        balance_line
    ).resolve_scale(
        y='shared'  # Share y-axis for IMA COD balance
    )


    # Combine both charts
    combined_chart = alt.layer(
        bar_chart,
        balance_combined
    ).resolve_scale(
        y='independent'  # Allow independent y-axes
    ).properties(
        title='IMA COD (Left & Right) and Imbalance'
    )

    return combined_chart


def team_individual_graph(filtered_df,filtered_df_week, metric):

    temp_df = filtered_df[["Player", "Position", f"{metric}"]].dropna()

    max_series = filtered_df_week.groupby(["Player"])[f"{metric}"].max()
    max_series.name = f"Max {metric}"
    max_series = max_series.reset_index()
    max_series.rename(columns={'index': 'Player'}, inplace=True)

    merged_df = temp_df.merge(max_series, on='Player', how='left')
    merged_df = merged_df.sort_values(by=metric, ascending=False)

    # Calculate the average Duration
    average_duration = merged_df[metric].mean()
    
    # Create the bar chart for Duration
    bars = alt.Chart(merged_df).mark_bar().encode(
        y=alt.Y('Player:N', sort=merged_df['Player'].tolist(), title='Player'),
        x=alt.X(f'{metric}:Q', title=metric),
        color=alt.Color('Position:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="Position")),
        tooltip=['Player', metric, f'{metric}']
    ).properties(
    height=800
)

    # Create the tick chart for Max Duration
    ticks = alt.Chart(merged_df).mark_tick(color='#FF4B4B', thickness=2, size=20).encode(
        y=alt.Y('Player:N', sort=merged_df['Player'].tolist(), title='Player'),
        x=alt.X(f'Max {metric}:Q')
    )

    # Create the dashed line for average Duration
    average_line = alt.Chart(pd.DataFrame({f'Avg {metric}': [average_duration]})).mark_rule(
        strokeDash=[5, 5], color='#A0DEFF'
    ).encode(
        x=f'Avg {metric}:Q'
    )

    # Combine the charts
    combined_chart = (bars + ticks + average_line).properties(
        title=f'{metric} vs Weekly Max {metric}'
    )

    return combined_chart

def create_sankey(df, date_range, column_name, node_positions=None, max_width=1000):
    # Filter DataFrame for the given date range
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Create a list of unique values in the specified column
    nodes = df_filtered[column_name].unique().tolist()
    
    # Initialize the Sankey diagram components
    node_labels = nodes
    links = {'source': [], 'target': [], 'value': [], 'player': [], 'date': []}
    
    # Create the links for the Sankey diagram
    previous_value = {}

    for date, group in df_filtered.groupby('Date'):
        current_value = group.set_index('Player')[column_name].to_dict()

        if previous_value:
            for player, value in current_value.items():
                if player in previous_value and previous_value[player] != value:
                    source_idx = nodes.index(previous_value[player])
                    target_idx = nodes.index(value)
                    links['source'].append(source_idx)
                    links['target'].append(target_idx)
                    links['value'].append(1)
                    links['player'].append(player)
                    links['date'].append(date.strftime('%Y-%m-%d'))

        previous_value = current_value

    # Extract positions for each node, setting default None for unspecified positions
    node_x = [node_positions[value][0] if node_positions and value in node_positions else None for value in node_labels]
    node_y = [node_positions[value][1] if node_positions and value in node_positions else None for value in node_labels]

    # Create the Sankey diagram with specified node positions
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=10,
            line=dict(color="black", width=0.5),
            label=node_labels,
            x=node_x,
            y=node_y
        ),
        link=dict(
            source=links['source'],
            target=links['target'],
            value=links['value'],
            customdata=list(zip(links['player'], links['date'])),
            hovertemplate='Player: %{customdata[0]}<br>Date: %{customdata[1]}<extra></extra>'
        )
    ))

    fig.update_layout(
        width=max_width,  # Set the maximum width
        title_text=f"Player Movements Between {column_name}s ({start_date.date()} to {end_date.date()})",
        font_size=10
    )
    return fig