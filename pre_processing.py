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
df = pd.read_csv("./data/anonymous.csv")

# Rename columns for reporting purpose
df.columns = ['Date', 'Player', 'Position', 'Team Name', 'Duration',
       'Total Distance(m)', 'Total Player Load', 'Acc 2m/s2 Total Effort',
       'Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort',
       'Dec 3m/s2 Total Effort', 'High Intensity Distance(m)',
       'Sprint Distance(m)', 'Maximum Velocity(m/s)', 'IMA COD(left)',
       'IMA COD(right)']


# %% Create a complete date range for each combination
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
unique_combinations = df[['Player', 'Position', 'Team Name']].drop_duplicates()
date_range = pd.date_range(start='2021-07-01', end='2023-06-30')
complete_data = pd.DataFrame()

# List of metrics to plot
metrics = ['Duration', 'Total Distance(m)', 'Total Player Load', 'Acc 2m/s2 Total Effort',
           'Acc 3m/s2 Total Effort', 'Dec 2m/s2 Total Effort', 'Dec 3m/s2 Total Effort',
           'High Intensity Distance(m)', 'Sprint Distance(m)', 'Maximum Velocity(m/s)',
           'IMA COD(left)', 'IMA COD(right)']

for _, row in unique_combinations.iterrows():
    player, position, team_name = row
    temp_df = pd.DataFrame({'Date': date_range})
    temp_df['Player'] = player
    temp_df['Position'] = position
    temp_df['Team Name'] = team_name
    complete_data = pd.concat([complete_data, temp_df], ignore_index=True)

merged_df = pd.merge(complete_data, df, on=['Date', 'Player', 'Position', 'Team Name'], how='left')

for column in metrics:
    merged_df[column] = merged_df[column].astype(float) 

df = merged_df.sort_values(by='Date')


# %% add season, weekday, week of year and year

def get_season(date):
    for season, (start_date, end_date) in seasons.items():
        if start_date <= date.strftime('%Y-%m-%d') <= end_date:
            return season
    return None

df['Season'] = df['Date'].apply(get_season)
df['Weekday'] = df['Date'].dt.day_name()
df['Week'] = df['Date'].dt.isocalendar().week
df['Year'] = df['Date'].dt.year


# %% create intensity metrics

df['Player Load Per Minute'] = df["Total Player Load"] / df["Duration"]
df["Distance Per Minute"] = df["Total Distance(m)"] / df["Duration"]

# %% Tool functions

# Calculate ACWR
def calc_acwr(df, metric):
    # The ACWR is the ratio between how much workload has been done 
    # in the last 7 days (acute workload) versus 
    # the average weekly workload that has been performed 
    # over the previous 28 days (chronic workload).
    # Calculated by Exponentially Weighted Moving Average
    # https://www.gpexe.com/2020/09/04/acutechronic-workload-ratio-part-2/

    pass

def is_load_abnormal(df, metric):
    # If 
    pass

def is_imbalance(df):
    pass