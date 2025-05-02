import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

import fastf1
import fastf1.plotting

import os
import time

cache_folder = 'cache_folder'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
fastf1.Cache.enable_cache(cache_folder)

fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                          color_scheme='fastf1')

year = int(input('Year ? '))
race_number = int(input('Race Number ? (1-24) '))
race_session = input('Session ? (R, S)')

session = fastf1.get_session(year, race_number, race_session)
session.load()

filename = f'../reports/reports/figures/{race_number}_{session.event["EventName"]}_{session.event.year}_Race/'
os.makedirs(os.path.dirname(filename), exist_ok=True)
os.chdir(filename)

event_name = session.event.EventName
circuit_info = session.get_circuit_info()
teams = fastf1.plotting.list_team_names(session)

def show_laptime_comp(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    if len(driver_1_laps) > 1 :
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps)>1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']

    last_lap = int(max(session.laps['LapNumber']))

    fig, ax = plt.subplots(figsize=(11, 5))
    
    ax.plot(driver_1_laps['LapNumber'], driver_1_laps['LapTime'], color=team_color)
    ax.plot(driver_2_laps['LapNumber'], driver_2_laps['LapTime'], color=team_color_2)
    ax.tick_params(labelright=True)
    ax.set_xlim([0, last_lap])
    
    plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)
    
    plt.grid(color='w', which='major', axis='both', linestyle='dotted')
    plt.savefig(fname=f'{session.name}_{team}_laptime_comp', transparent=True)
    
def show_laptime_scatterplot(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
    
    if driver_1_laps.empty:
        min_laptime = min(driver_2_laps['LapTime'])
        max_laptime = max(driver_2_laps['LapTime'])
    elif driver_2_laps.empty:
        min_laptime = min(driver_1_laps['LapTime'])
        max_laptime = max(driver_1_laps['LapTime'])
    else:
        min_laptime = min(min(driver_1_laps['LapTime']), min(driver_2_laps['LapTime']))
        max_laptime = max(max(driver_1_laps['LapTime']), max(driver_2_laps['LapTime']))
    
    min_laptime = min_laptime - \
                        timedelta(seconds= 1)
    max_laptime = max_laptime + \
                        timedelta(seconds= 1)
    
    last_lap = int(max(session.laps['LapNumber'])) + 1
    
    fig, ax = plt.subplots(figsize=(5.75, 4.2))
    
    sns.scatterplot(data=driver_1_laps,
                    x="LapNumber",
                    y="LapTime",
                    hue = 'Compound',
                    palette=fastf1.plotting.get_compound_mapping(session=session),
                    edgecolor = team_color,
                    style="Compound",
                    s=50,
                    linewidth=0.5)
    
    sns.scatterplot(data=driver_2_laps,
                    x="LapNumber",
                    y="LapTime",
                    hue = 'Compound',
                    palette=fastf1.plotting.get_compound_mapping(session=session),
                    edgecolor = team_color_2,
                    style="Compound",
                    s=50,
                    linewidth=0.5)
    
    ax.invert_yaxis()
    ax.tick_params(labelleft=False)
    ax.set_xlim([0, last_lap])
    ax.set(xlabel=None)
    ax.set(ylabel=None)
    ax.set_ylim([min_laptime, max_laptime])
    plt.tick_params(left = False)
    plt.tick_params(bottom = False)
    plt.legend(frameon=False)
    plt.grid(color='w', which='major', axis='both', linestyle='dotted')

    plt.tight_layout()
    plt.savefig(fname=f'{session.name}_{team}_laptime_scatterplot', transparent=True)

    
def show_pace_comp(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()

    driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
    
    transformed_driver_1_laps = driver_1_laps.copy()
    transformed_driver_1_laps.loc[:, "LapTime (s)"] = driver_1_laps["LapTime"].dt.total_seconds()
    transformed_driver_2_laps = driver_2_laps.copy()
    transformed_driver_2_laps.loc[:, "LapTime (s)"] = driver_2_laps["LapTime"].dt.total_seconds()
    
    if transformed_driver_1_laps.empty:
        min_laptime = min(transformed_driver_2_laps['LapTime'])
        max_laptime = max(transformed_driver_2_laps['LapTime'])
    elif transformed_driver_2_laps.empty:
        min_laptime = min(transformed_driver_1_laps['LapTime'])
        max_laptime = max(transformed_driver_1_laps['LapTime'])
    else:
        min_laptime = min(min(transformed_driver_1_laps['LapTime']), min(transformed_driver_2_laps['LapTime']))
        max_laptime = max(max(transformed_driver_1_laps['LapTime']), max(transformed_driver_2_laps['LapTime']))
    min_laptime = min_laptime - \
                        timedelta(seconds= 1)
    max_laptime = max_laptime + \
                        timedelta(seconds= 1)
                        
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    plt.rcParams.update({'font.size': 12})

    sns.boxplot(
        data=transformed_driver_1_laps,
        y="LapTime",
        color = team_color,
        linecolor = 'white',
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )
    

    plt.grid(visible=False)
    ax.tick_params(bottom=False)
    ax.invert_yaxis()
    ax.set(xlabel=None)
    ax.set(ylabel=None)
    ax.set_ylim([min_laptime, max_laptime])
    
    plt.tick_params(bottom = False)
    plt.grid(color='w', which='major', axis='y', linestyle = 'dotted')
    plt.tight_layout()
    plt.savefig(fname=f'{session.name}_{team}_driver_1_pace', transparent=True)

    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    sns.boxplot(
        data=transformed_driver_2_laps,
        y="LapTime",
        color = team_color_2,
        linecolor = 'white',
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )

    plt.grid(visible=False)

    ax.yaxis.tick_right()
    ax.tick_params(bottom=False)
    plt.xticks(visible=False)
    ax.invert_yaxis()
    ax.set(xlabel=None)
    ax.set(ylabel=None)
    ax.set_ylim([min_laptime, max_laptime])
 
    plt.grid(color='w', which='major', axis='y', linestyle = 'dotted')
    plt.tight_layout()
    plt.savefig(fname=f'{session.name}_{team}_driver_2_pace', transparent=True)

    
def show_tyre_strategy(team_drivers, session):
    fig, ax = plt.subplots(figsize=(9.2, 1.2))
    
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+2))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+2))).reset_index()
    if len(driver_1_laps) > 1 :
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps)>1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
    last_lap = int(max(session.laps['LapNumber']))
    
    for driver in team_drivers:
        laps = session.laps.pick_drivers(driver)
        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"],
                                                                session=session)
            plt.barh(
                y=driver,
                width=row["StintLength"],
                height = 0.4,
                align='center',
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black",
                fill=True
            )

            previous_stint_end += row["StintLength"]

    plt.grid(False)
    plt.grid(color='w', which='major', axis='x', linestyle='dotted')

    ax.xaxis.tick_top()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xlim([0, last_lap])

    plt.tight_layout()
    plt.savefig(fname=f'{session.name}_{team}_tyre_strategy', transparent=True)

for idx,team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    team_color = fastf1.plotting.get_team_color(team, session=session)
    df_color=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/second_color.csv", index_col='team')
    team_color_2 = df_color.iat[idx,0]
    try:
        show_pace_comp(team_drivers, session)
        show_laptime_scatterplot(team_drivers, session)
        show_laptime_comp(team_drivers, session)
        show_tyre_strategy(team_drivers, session)
    except:
        print(f'No data for {team}')