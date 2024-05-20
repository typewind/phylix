# %%
import pandas as pd
import numpy as np
import re
import os
import datetime

# %% Pre-defined season
seasons = {
    "2021/22": ('2021-07-01', '2022-06-30'),
    "2022/23": ('2022-07-01', '2023-06-30')
}


# %% Read data and rename columns
df_all = pd.read_csv("./data/anonymous.csv")

# Rename columns for reporting purpose
df_all.columns = ['Date', 'Player', 'Position', 'Team Name', 'Duration',
       'Total Distance(m)', 'Total Player Load', 'Acc 2m/s2 Total Effort',
       'Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort',
       'Dec 3m/s2 Total Effort', 'High Intensity Distance(m)',
       'Sprint Distance(m)', 'Maximum Velocity(m/s)', 'IMA COD(left)',
       'IMA COD(right)']


# %% Tool functions

# Calculate ACWR
def calc_ewma_acwr(df, metric, acute_days=7, chronic_days=28):
    # The ACWR is the ratio between how much workload has been done 
    # in the last 7 days (acute workload) versus 
    # the average weekly workload that has been performed 
    # over the previous 28 days (chronic workload).
    # Calculated by Exponentially Weighted Moving Average
    # https://www.gpexe.com/2020/09/04/acutechronic-workload-ratio-part-2/
    
    # Function to calculate EWMA
    def ewma(series, span):
        return series.ewm(span=span, adjust=False).mean()
    
    temp_df = df.copy()

    # Calculate EWMA ACWR for each player
    temp_df[f'{metric} Acute EWMA'] = temp_df.groupby('Player')[metric].transform(lambda x: ewma(x, acute_days))
    temp_df[f'{metric} Chronic EWMA'] = temp_df.groupby('Player')[metric].transform(lambda x: ewma(x, chronic_days))
    df[f'{metric} EWMA ACWR'] = temp_df[f'{metric} Acute EWMA']/temp_df[f'{metric} Chronic EWMA']

    return df


def is_load_abnormal(df, metric):
    conditions = [
        (df[f'{metric} EWMA ACWR'] > 1.3),
        (df[f'{metric} EWMA ACWR'] < 0.8),
        (df[f'{metric} EWMA ACWR'] >= 0.8) & (df[metric] <= 1.3)
    ]
    choices = ['High', 'Low', 'Moderate']
    
    # Apply the classification
    df[f'is_{metric}_abnormal'] = np.select(conditions, choices, default='Moderate')
    
    return df


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
                                                {wch_colour_box[2]}, 0.75); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}, 0.75); 
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


def get_training_intensity(df):
    df['Load Per Minute'] = df["Total Player Load"] / df["Duration"]
    df["Distance Per Minute"] = df["Total Distance(m)"] / df["Duration"]
    return df

def get_imbalance(df):
    df["IMA COD Imbalance"] = (df['IMA COD(left)'] - df['IMA COD(right)'])/df['IMA COD(right)']
    return df

# %% Create a complete date range for each combination
df_all['Date'] = pd.to_datetime(df_all['Date'], format='%d/%m/%Y')
unique_combinations = df_all[['Player', 'Position', 'Team Name']].drop_duplicates()
date_range = pd.date_range(start='2021-07-01', end='2023-06-30')
complete_data = pd.DataFrame()

# List of metrics to plot
metrics = ['Duration', 'Total Distance(m)', 'Total Player Load', 'Acc 2m/s2 Total Effort',
           'Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort', 'Dec 3m/s2 Total Effort',
           'High Intensity Distance(m)', 'Sprint Distance(m)', 'Maximum Velocity(m/s)',
           'IMA COD(left)', 'IMA COD(right)']

intensity_metrics = ['Load Per Minute', 'Distance Per Minute']

for _, row in unique_combinations.iterrows():
    player, position, team_name = row
    temp_df = pd.DataFrame({'Date': date_range})
    temp_df['Player'] = player
    temp_df['Position'] = position
    temp_df['Team Name'] = team_name
    complete_data = pd.concat([complete_data, temp_df], ignore_index=True)

merged_df = pd.merge(complete_data, df_all, on=['Date', 'Player', 'Position', 'Team Name'], how='left')

for column in metrics:
    merged_df[column] = merged_df[column].astype(float) 

df_all = merged_df.sort_values(by='Date')


# %% add season, weekday, week of year and year

def get_season(date):
    for season, (start_date, end_date) in seasons.items():
        if start_date <= date.strftime('%Y-%m-%d') <= end_date:
            return season
    return None

df_all['Season'] = df_all['Date'].apply(get_season)
df_all['Weekday'] = df_all['Date'].dt.day_name()
df_all['Week'] = df_all['Date'].dt.isocalendar().week
df_all['Year'] = df_all['Date'].dt.year
df_all['Year-Week'] = df_all['Year'].astype(str) + '-W' + df_all['Week'].astype(str).str.zfill(2)

df_week_player = df_all.groupby(["Player", "Position", "Team Name", "Season", "Year", "Week", "Year-Week"])[metrics].mean()
df_week_team = df_all.groupby(["Team Name", "Season", "Year", "Week", "Year-Week"])[metrics].mean()

# %% create intensity metrics

df_all = get_training_intensity(df_all)
df_week_player = get_training_intensity(df_week_player)
df_week_team = get_training_intensity(df_week_team)

# %% calculate imbalance of IMA COD

df_all = get_imbalance(df_all)
df_week_player = get_imbalance(df_week_player)


# %% calculate EWMA ACWR
for metric in metrics+intensity_metrics:
    df_all = calc_ewma_acwr(df_all, metric)
    df_week_player = calc_ewma_acwr(df_week_player, metric, acute_days=1, chronic_days=4)

# %% find abnormal per player
for metric in metrics + intensity_metrics:
    df_all = is_load_abnormal(df_all, metric)
    df_week_player = is_load_abnormal(df_week_player, metric)





# %%
