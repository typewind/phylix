import altair as alt
import pandas as pd
import datetime
import time

metrics_classes = {
    "Intensity": ['Load Per Minute', 'Distance Per Minute'],
    "Agility": ['Acc 2m/s2 Total Effort','Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort', 'Dec 3m/s2 Total Effort'],
    "IMA": ['IMA COD(left)', 'IMA COD(right)'],
    "Volumn": ['Duration', 'Total Distance(m)', 'Total Player Load']
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
    alt.Y(f'{col} EWMA ACWR'),
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
        title=f"{col} vs EWMA ACWR"
    )

    return combined_chart


def get_not_passed_metrics(df, metrics_classes):
    not_pass_metrics = {}
    for key, value in metrics_classes.items():
        not_pass = [metric for metric in value if any(df.head(8)[f"is_{metric}_abnormal"]!="Moderate")]
        not_pass_metrics[key] = not_pass
    return metrics_classes



def submit_comment(player_id,  text, comment_table):
    ts = time.time()
    now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame({'Player ID': [player_id], 'Timestamp': [now], 'Comment': [text]})
    comment_table = pd.concat([comment_table, new_row], ignore_index=True)
    comment_table.to_csv("./data/player_weekly_review_comment.csv", encoding='utf-8', index=False)