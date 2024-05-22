# %%
import pandas as pd
import numpy as np
import re
import os
import datetime
from tools import metrics_classes

# %% Pre-defined variables
IMBA_THRES = 0.1

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
def calc_ewma_acwr(df, metric, acute_days=7, chronic_days=21, min_periods=28):
    # The ACWR is the ratio between how much workload has been done 
    # in the last 7 days (acute workload) versus 
    # the average weekly workload that has been performed 
    # over the previous 21 days (chronic workload).
    # Calculated by Exponentially Weighted Moving Average
    # https://support.catapultsports.com/hc/en-us/articles/360000538795-How-to-Set-Up-an-Acute-Chronic-Workload-Ratio-Chart
    
    # Function to calculate EWMA
    def ewma(series, span):
        return series.ewm(span=span, adjust=True).mean()
    
    temp_df = df.copy()

    # Calculate EWMA ACWR for each player
    temp_df[f'{metric} Acute EWMA'] = temp_df.groupby('Player')[metric].transform(lambda x: ewma(x, acute_days))
    temp_df[f'{metric} Chronic EWMA'] = temp_df.groupby('Player')[metric].transform(lambda x: ewma(x, chronic_days))
    df[f'{metric} EWMA ACWR'] = (temp_df[f'{metric} Acute EWMA']/temp_df[f'{metric} Chronic EWMA']).round(2)

    return df


def is_load_abnormal(df, metric):
    conditions = [
        (df[f'{metric} EWMA ACWR'] > 1.5),
        (df[f'{metric} EWMA ACWR'] < 0.8),
        (df[f'{metric} EWMA ACWR'] >= 0.8) & (df[metric] <= 1.5)
    ]
    choices = ['High', 'Low', 'Moderate']
    
    # Apply the classification
    df[f'is_{metric}_abnormal'] = np.select(conditions, choices, default='Moderate')
    return df

def get_risk_score(df, metrics, risk_score_name):
        # Convert classification results to numerical values
    classification_to_num = {'High': 1, 'Low': 1, 'Moderate': 0}
    for metric in metrics:
        df[f'{metric}_abnormal_num'] = df[f'is_{metric}_abnormal'].map(classification_to_num)
    df[risk_score_name] = df[[f'{metric}_abnormal_num' for metric in metrics]].sum(axis=1)
    df.drop(columns=[f'{metric}_abnormal_num' for metric in metrics], inplace=True)
    return df


def get_training_intensity(df):
    df['Load Per Minute'] = (df["Total Player Load"] / df["Duration"]).round(2)
    df["Distance Per Minute"] = (df["Total Distance(m)"] / df["Duration"]).round(2)
    df["Acc-Dec-COD Per Minute"] = ((df['IMA COD(left)'] + df['IMA COD(right)'] + 
                                    df['Acc 2m/s2 Total Effort'] + df['Dec 2m/s2 Total Effort']
                                    )/ df["Duration"]).round(2)
    return df

def get_imbalance(df):
    df["IMA COD Imbalance"] = ((df['IMA COD(left)'] - df['IMA COD(right)'])/df['IMA COD(right)']).round(2)
    df["Is IMA Imbalance"] = df["IMA COD Imbalance"].abs() > IMBA_THRES

    conditions = [
        (df["IMA COD Imbalance"] > 1.2),
        (df["IMA COD Imbalance"] < 0.8),
        (df["IMA COD Imbalance"] >= 0.8) & (df["IMA COD Imbalance"] <= 1.2)
    ]
    choices = ['Left', 'Right', 'Balance']
    df["IMA COD Deviation"] = np.select(conditions, choices, default='Balance')
    df["IMA COD(Right) %"] = (df['IMA COD(right)'] / (df['IMA COD(left)'] + df['IMA COD(right)'])).apply(lambda x: f"{x:.2%}")
    df["IMA COD(Left) %"] = (df['IMA COD(left)'] / (df['IMA COD(left)'] + df['IMA COD(right)'])).apply(lambda x: f"{x:.2%}")
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


# metrics classification
intensity_metrics = ['Load Per Minute', 'Distance Per Minute', 'Acc-Dec-COD Per Minute']

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

df_week_player = df_all.groupby(["Player", "Position", "Team Name", "Year", "Week", "Year-Week"])[metrics].mean()
df_week_team = df_all.groupby(["Team Name", "Year", "Week", "Year-Week"])[metrics].mean()


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
    df_week_player = calc_ewma_acwr(df_week_player, metric, acute_days=1, chronic_days=3, min_periods=3)

# %% find abnormal per player
for metric in metrics + intensity_metrics:
    df_all = is_load_abnormal(df_all, metric)
    df_week_player = is_load_abnormal(df_week_player, metric)

# %% calculate risk score
for metric_class, metrics in metrics_classes.items():
    df_all = get_risk_score(df_all, metrics, f"{metric_class} Risk Score")
    df_week_player = get_risk_score(df_week_player, metrics, f"{metric_class} Risk Score")

# %%
df_week_player = df_week_player.reset_index()
df_week_team = df_week_team.reset_index()

# %% add date to week player and team for filter
def year_week_to_date(year, week):
    first_day_of_year = datetime.datetime(year, 1, 1)
    first_day_of_week = first_day_of_year - datetime.timedelta(days=first_day_of_year.weekday())
    start_of_week = first_day_of_week + datetime.timedelta(weeks=week)
    return start_of_week

df_week_player['Date'] = df_week_player.apply(lambda row: year_week_to_date(row['Year'], row['Week']), axis=1)
df_week_team['Date'] = df_week_team.apply(lambda row: year_week_to_date(row['Year'], row['Week']), axis=1)

df_week_player['Season'] = df_week_player['Date'].apply(get_season)
df_week_team['Season'] = df_week_team['Date'].apply(get_season)


# %% export to csv
df_all.to_csv("./data/df_all.csv", index=False, encoding="utf-8-sig")
df_week_player.to_csv("./data/df_week_player.csv", index=False, encoding="utf-8-sig")
df_week_team.to_csv("./data/df_week_team.csv", index=False, encoding="utf-8-sig")
# %%
