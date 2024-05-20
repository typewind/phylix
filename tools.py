import altair as alt
import pandas as pd


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

def melt_df(col, df):
    df_l = df[["Datetime UTC", f'L {col}', f'L {col}_mean']]
    df_l.columns = ["Datetime UTC", col, f'{col}_mean']
    df_l["Foot"] = "L"

    df_r = df[["Datetime UTC", f'R {col}', f'R {col}_mean']]
    df_r.columns = ["Datetime UTC", col, f'{col}_mean']
    df_r["Foot"] = "R"

    return pd.concat([df_l, df_r])

def draw_alt(source, col):
    source_m = melt_df(col, source)
    selection = alt.selection_multi(fields=['Foot'], bind='legend')
    interval = alt.selection_interval(encodings=['x'])


    avg_L = alt.Chart(source_m).mark_line(strokeDash=[1,3]).encode(
    alt.X("Datetime UTC"),
    alt.Y(f'{col}_mean'),
    alt.Color("Foot"),
    )
    
    chart = alt.Chart(source_m).mark_line(point=True).encode(
        alt.X("Datetime UTC"),
        alt.Y(col, axis=alt.Axis(title=f'{col}')),
        alt.Color("Foot"),
        alt.Tooltip([col, "Foot"]),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        ).add_selection(selection
                        ).properties(width=300, height=300
                        ).interactive()
    
    return chart + avg_L
