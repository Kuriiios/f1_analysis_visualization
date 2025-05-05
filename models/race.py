import seaborn as sns
from matplotlib import pyplot as plt
from datetime import timedelta

import fastf1
import fastf1.plotting
from fastf1.ergast import Ergast

import os
import csv

import pandas as pd
import numpy as np
import ast

from matplotlib.ticker import FuncFormatter
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement

ergast = Ergast()

cache_folder = 'cache_folder'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
fastf1.Cache.enable_cache(cache_folder)

fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                          color_scheme='fastf1')

year = int(input('Year ? '))
race_number = int(input('Race Number ? (1-24) '))
race_session = input('Session ? (R, S) ')

session = fastf1.get_session(year, race_number, race_session)
session.load()

filename = f'/home/kurios/Documents/f1_analysis/reports/figures/{race_number}_{session.event["EventName"]}_{session.event.year}_Race/'
os.makedirs(os.path.dirname(filename), exist_ok=True)
os.chdir(filename)

pit = ergast.get_pit_stops(season = year, round = race_number )
event_name = session.event.EventName
circuit_info = session.get_circuit_info()
teams = fastf1.plotting.list_team_names(session)

def seconds_to_mmss(x, pos):
    minutes = int(x // 60)
    seconds = x % 60
    return f"{minutes}:{seconds:05.2f}"

def show_laptime_comp(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    if len(driver_1_laps) > 1 :
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps)>1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']

    last_lap = int(max(session.laps['LapNumber']))

    fig, ax = plt.subplots(figsize=(10, 5))
    
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
    os.chdir(filename)
    plt.savefig(fname=f'{session.name}_{team}_laptime_comp', transparent=True)
    
def show_laptime_scatterplot(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber']))+1))).reset_index()

    if len(driver_1_laps) > 1:
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps) > 1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
   
    driver_1_valid = driver_1_laps['LapTime'].dropna()
    driver_2_valid = driver_2_laps['LapTime'].dropna()

    if driver_1_valid.empty and driver_2_valid.empty:
        print("No valid lap times to display.")
        return
    elif driver_1_valid.empty:
        min_laptime = min(driver_2_valid)
        max_laptime = max(driver_2_valid)
    elif driver_2_valid.empty:
        min_laptime = min(driver_1_valid)
        max_laptime = max(driver_1_valid)
    else:
        min_laptime = min(min(driver_1_valid), min(driver_2_valid))
        max_laptime = max(max(driver_1_valid), max(driver_2_valid))
    
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
    os.chdir(filename)
    plt.savefig(fname=f'{session.name}_{team}_laptime_scatterplot', transparent=True)

    
def show_pace_comp(team_drivers, session):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()

    if len(driver_1_laps) > 1:
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps) > 1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']

    transformed_driver_1_laps = driver_1_laps.copy()
    transformed_driver_2_laps = driver_2_laps.copy()
    transformed_driver_1_laps["LapTime"] = transformed_driver_1_laps["LapTime"].dt.total_seconds()
    transformed_driver_2_laps["LapTime"] = transformed_driver_2_laps["LapTime"].dt.total_seconds()

    all_laptimes = []
    if not transformed_driver_1_laps.empty:
        all_laptimes.extend(transformed_driver_1_laps["LapTime"].dropna())
    if not transformed_driver_2_laps.empty:
        all_laptimes.extend(transformed_driver_2_laps["LapTime"].dropna())

    if not all_laptimes:
        print("No valid lap times to display.")
        return

    min_laptime = min(all_laptimes) - 1
    max_laptime = max(all_laptimes) + 1

    plt.rcParams.update({
        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': False,
        'font.size': 12
    })

    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    if "LapTime" in transformed_driver_1_laps.columns and transformed_driver_1_laps["LapTime"].dropna().size > 0:
        sns.boxplot(
            data=transformed_driver_1_laps,
            y="LapTime",
            color=team_color,
            linecolor='white',
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )

    ax.set_ylim([max_laptime, min_laptime])
    ax.invert_yaxis()
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(bottom=False)
    ax.yaxis.set_major_formatter(FuncFormatter(seconds_to_mmss))

    plt.xticks(visible=False)
    plt.grid(color='w', which='major', axis='y', linestyle='dotted')
    plt.tight_layout()
    os.chdir(filename)
    plt.savefig(fname=f'{session.name}_{team}_driver_1_pace', transparent=True)

    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    if "LapTime" in transformed_driver_2_laps.columns and transformed_driver_2_laps["LapTime"].dropna().size > 0:
        sns.boxplot(
            data=transformed_driver_2_laps,
            y="LapTime",
            color=team_color_2,
            linecolor='white',
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )

    ax.set_ylim([max_laptime, min_laptime])
    ax.invert_yaxis()
    ax.set(xlabel=None, ylabel=None)
    ax.yaxis.tick_right()
    ax.tick_params(bottom=False)
    ax.yaxis.set_major_formatter(FuncFormatter(seconds_to_mmss))

    plt.xticks(visible=False)
    plt.grid(color='w', which='major', axis='y', linestyle='dotted')
    plt.tight_layout()
    os.chdir(filename)
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
    os.chdir(filename)
    plt.savefig(fname=f'{session.name}_{team}_tyre_strategy', transparent=True)
    
def get_pitstop_time(session, team_drivers):
    driver_1_name = fastf1.plotting.get_driver_name(team_drivers[0], session).split()[1].lower()
    driver_2_name = fastf1.plotting.get_driver_name(team_drivers[1], session).split()[1].lower()
    if driver_1_name == 'verstappen':
        driver_1_name = 'max_verstappen'
    pit0 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_1_name).content
    pit1 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_2_name).content
    
    try:
        pit0_number = str(pit0[0]['stop'].iloc[-1])
        pit0_total_duration = str(pit0[0]['duration'].sum())[10:-3]+ ' s'
    except:
        pit0_number = '0'
        pit0_total_duration = str(timedelta(0))
    try:
        pit1_number = str(pit1[0]['stop'].iloc[-1])
        pit1_total_duration = str(pit1[0]['duration'].sum())[10:-3]+ ' s'
    except:
        pit1_number = '0'
        pit1_total_duration = str(timedelta(0))
        
    return pit0_number, pit0_total_duration, pit1_number, pit1_total_duration

def get_faster_driver_per_lap(session, team_drivers):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, session.total_laps+1)).reset_index()
    
    if len(driver_1_laps) > 1:
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps) > 1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
        
    fastest_driver_per_lap = []
    if len(driver_1_laps) == len(driver_2_laps):
        for lap in range(len(driver_1_laps)):
            if '4' in str(driver_1_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver_1_laps['LapTime'][lap] < driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver_1_laps['LapTime'][lap] > driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
    elif len(driver_1_laps) > len(driver_2_laps):
        for lap in range(len(driver_2_laps)):
            if '4' in str(driver_1_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver_1_laps['LapTime'][lap] < driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver_1_laps['LapTime'][lap] > driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
        for lap in range(len(driver_2_laps), len(driver_1_laps)):
            if '4' in str(driver_1_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            else:
                fastest_driver_per_lap.append(0)
    elif len(driver_1_laps) < len(driver_2_laps):
        for lap in range(len(driver_1_laps)):
            if '4' in str(driver_1_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver_1_laps['LapTime'][lap] < driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver_1_laps['LapTime'][lap] > driver_2_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
        for lap in range(len(driver_1_laps), len(driver_2_laps)):
            if '4' in str(driver_2_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            else:
                fastest_driver_per_lap.append(1)    
    return fastest_driver_per_lap

def get_lap_repartition(fastest_driver_per_lap):
    driver_1_faster = str(fastest_driver_per_lap.count(0))+ '/' + str(len(fastest_driver_per_lap))
    driver_2_faster = str(fastest_driver_per_lap.count(1))+ '/' + str(len(fastest_driver_per_lap))
    safety_car_lap = str(fastest_driver_per_lap.count(2))+ '/' + str(len(fastest_driver_per_lap))

    team_info = [
        driver_1_faster,
        driver_2_faster,
        safety_car_lap,
        fastest_driver_per_lap
        ]
    return team_info

def get_final_gap(session, team_drivers):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, session.total_laps+1)).reset_index()
    
    if len(driver_1_laps) > 1:
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps) > 1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
        
    zero_time = timedelta(0)
    if len(driver_1_laps) == len(driver_2_laps):
        if driver_1_laps['Time'].iloc[-1] > driver_2_laps['Time'].iloc[-1]:
            gap = str(driver_1_laps['Time'].iloc[-1] - driver_2_laps['Time'].iloc[-1])[7:]
            driver_1_gap = '+' + str(gap)[3:-3] + ' s'
            driver_2_gap = '-' + str(gap)[3:-3] + ' s'
        elif driver_1_laps['Time'].iloc[-1] < driver_2_laps['Time'].iloc[-1]:
            gap = pd.to_timedelta(zero_time - (driver_1_laps['Time'].iloc[-1] - driver_2_laps['Time'].iloc[-1])).total_seconds()
            driver_1_gap = '-' + str(gap) + ' s'
            driver_2_gap = '+' + str(gap) + ' s'
            
    elif len(driver_1_laps) > len(driver_2_laps):
        gap = len(driver_1_laps) - len(driver_2_laps)
        driver_1_gap = '-' + str(gap) + ' laps'
        driver_2_gap = '+' + str(gap) + ' laps'
    elif len(driver_1_laps) < len(driver_2_laps):
        gap = len(driver_2_laps) - len(driver_1_laps)
        driver_1_gap = '+' + str(gap) + ' laps'
        driver_2_gap = '-' + str(gap) + ' laps'
    if driver_1_gap[1:4] == '00:':
        driver_1_gap = driver_1_gap[0] + driver_1_gap[4:]
    if driver_2_gap[1:4] == '00:':
        driver_2_gap = driver_2_gap[0] + driver_2_gap[4:]
        
    return driver_1_gap, driver_2_gap

def get_drivers_info(session,team_drivers):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_quicklaps(1.4).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_quicklaps(1.4).reset_index()
    
    if len(driver_1_laps) > 1:
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps) > 1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']

    driver_1_name = fastf1.plotting.get_driver_name(team_drivers[0], session)
    driver_2_name = fastf1.plotting.get_driver_name(team_drivers[1], session)
    if driver_1_name == 'Andrea Kimi Antonelli':
        driver_1_name = 'Kimi Antonelli'
    if driver_2_name == 'Andrea Kimi Antonelli':
        driver_2_name = 'Kimi Antonelli'
    if driver_1_name == 'Oliver Bearman':
        driver_1_name = 'Ollie Bearman'
    if driver_2_name == 'Oliver Bearman':
        driver_2_name = 'Ollie Bearman'
    
    driver_1_gap, driver_2_gap = get_final_gap(session, team_drivers)
    if race_session == 'R':
        pit0_number, pit0_total_duration, pit1_number, pit1_total_duration = get_pitstop_time(session, team_drivers)
    elif race_session == 'S':
        pit0_number = 0
        pit0_total_duration = timedelta(0)
        pit1_number = '0'
        pit1_total_duration = timedelta(0)
    
    try :
        driver_1_position = int(driver_1_laps['Position'].iloc[-1])
    except:
        driver_1_position = 'DNF'

    try:
        driver_2_position = int(driver_2_laps['Position'].iloc[-1])
    except:
        driver_2_position = 'DNF'
        
    try:
        driver_1_laps['LapTime'] = driver_1_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_1 = str(driver_1_laps['Time'].iloc[-1] - driver_1_laps['Time'][0])[8:-3]
        driver_1_avg_lap = str(timedelta(seconds = driver_1_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_1_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver_1_iqr = str(round(q3 - q1, 3))+ ' s'
    except:
        race_time_driver_1 = 0
        driver_1_avg_lap= 0
        driver_1_iqr= str('0')
        
    try:
        driver_2_laps['LapTime'] = driver_2_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_2 = str(driver_2_laps['Time'].iloc[-1] - driver_2_laps['Time'][0])[8:-3]        
        driver_2_avg_lap = str(timedelta(seconds = driver_2_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_2_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver_2_iqr = str(round(q3 - q1, 3))+ ' s'

    except:
        race_time_driver_2 = 0
        driver_2_avg_lap= 0
        driver_2_iqr= str(0)
        
    drivers_info = [
        driver_1_name,
        driver_1_position,
        driver_1_gap,
        race_time_driver_1,
        driver_1_avg_lap,
        driver_1_iqr,
        pit0_number,
        pit0_total_duration,
        driver_2_name,
        driver_2_position,
        driver_2_gap,
        race_time_driver_2,
        driver_2_avg_lap,
        driver_2_iqr,
        pit1_number,
        pit1_total_duration,
    ]
    return drivers_info
    
def create_csv_race_info(session, team, list, drivers_info, team_info):
    race_info_csv = list
    df_logo=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/team_logo.csv", index_col='team')
    if race_session == 'R':
        event_title = event_name.split(' ', 1)[0]+ ' GP Race '
    elif race_session == 'S':
        event_title = event_name.split(' ', 1)[0]+ ' GP Sprint Race '
    race_info = [
        event_title,
    ]
    race_info.extend(drivers_info)
    race_info.extend(team_info)
    race_info_csv.append(race_info)
    return race_info_csv

def SubElement(parent, tagname, **kwargs):
        element = OxmlElement(tagname)
        element.attrib.update(kwargs)
        parent.append(element)
        return element

def _set_shape_transparency(shape, alpha):
    """ Set the transparency (alpha) of a shape"""
    ts = shape.fill._xPr.solidFill
    sF = ts.get_or_change_to_srgbClr()
    sE = SubElement(sF, 'a:alpha', val=str(alpha))
    
def Hex_RGB(ip):
    return tuple(int(ip[i+1:i+3],16) for i in (0, 2, 4))

def to_str(var):
    return str(list(np.reshape(np.asarray(var), (1, np.size(var)))[0]))[1:-1]
    
for idx,team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    team_color = fastf1.plotting.get_team_color(team, session=session)
    df_color=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/second_color.csv", index_col='team')
    team_color_2 = df_color.iat[idx,0]
    show_pace_comp(team_drivers, session)
    show_laptime_scatterplot(team_drivers, session)
    show_laptime_comp(team_drivers, session)
    show_tyre_strategy(team_drivers, session)
    

laptime_scatterplot = {}
laptime_comp = {}
tyre_strategy = {}
pace_comp0 = {}
pace_comp1 = {}

csv_file_path = f'{race_number}_{race_session}_race_info.csv'
csv_file_path_fastest_driver = f'{race_number}_{race_session}_race_fastest_driver.csv'

lap_info_per_team = [['EventName', 'driver_1_name', 'driver_1_position', 'driver_1_gap', 'total_time_driver_1', 'avg_laptime_driver_1','iqr_driver_1', 'number_pit_driver_1', 'total_duration_pit_driver_1', 'driver_2_name', 'driver_2_position', 'driver_2_gap', 'total_time_driver_2', 'avg_laptime_driver_2','iqr_driver_2', 'number_pit_driver_2', 'total_duration_pit_driver_2', 'fastest_driver_1', 'fastest_driver_2', 'safety_car_lap', 'fastest_lap']]
race_info = []
fastest_driver_per_lap_dict = {}
for idx,team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    drivers_info = get_drivers_info(session, team_drivers)
    fastest_driver_per_lap_per_team = get_faster_driver_per_lap(session, team_drivers)
    fastest_driver_per_lap_dict.update({f'{team}':fastest_driver_per_lap_per_team})
    team_info = get_lap_repartition( fastest_driver_per_lap_per_team)
    race_info = create_csv_race_info(session, team, lap_info_per_team, drivers_info, team_info)
os.chdir('/home/kurios/Documents/f1_analysis/reports/csv')
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(race_info)
    
figures_path = '/home/kurios/Documents/f1_analysis/reports/figures/'
if race_session == 'R':
    race_session_name = 'Race'
elif race_session == 'S':
    race_session_name = 'Sprint'

path = '/home/kurios/Documents/f1_analysis/reports/csv/'

keyword = f'{race_number}_{race_session}_race_info'
for fname in os.listdir(path):
    if keyword in fname:
        driver_data = fname
os.chdir(path)
arr = pd.read_csv(driver_data)

counter = 0
prs = Presentation()

for idx, team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    team_color = fastf1.plotting.get_team_color(team, session=session)
    df_color=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/second_color.csv", index_col='team')
    team_color_2 = df_color.iat[idx,0]
    team_color = Hex_RGB(team_color)
    team_color_2 = Hex_RGB(team_color_2)
    
    if team_drivers[0] in  session.laps['Driver'].values and team_drivers[1] in  session.laps['Driver'].values:
        try:
            race_name = arr.iloc[counter]['EventName']
            os.chdir(figures_path)
            team_logo = f'/home/kurios/Documents/f1_analysis/data/external/team_logos/{team}.png'
            os.chdir(figures_path)
            laptime_comp = f'{race_number}_{event_name}_{year}_{race_session_name}/{race_session_name}_{team}_laptime_comp.png'
            os.chdir(figures_path)
            laptime_scatterplot = f'{race_number}_{event_name}_{year}_{race_session_name}/{race_session_name}_{team}_laptime_scatterplot.png'
            os.chdir(figures_path)
            tyre_strategy = f'{race_number}_{event_name}_{year}_{race_session_name}/{race_session_name}_{team}_tyre_strategy.png'
            os.chdir(figures_path)
            driver_1_pace = f'/{race_number}_{event_name}_{year}_{race_session_name}/{race_session_name}_{team}_driver_1_pace.png'
            os.chdir(figures_path)
            driver_2_pace = f'/{race_number}_{event_name}_{year}_{race_session_name}/{race_session_name}_{team}_driver_2_pace.png'
            
            name_driver_1 = arr.iloc[counter]['driver_1_name']
            driver_1_position = arr.iloc[counter]['driver_1_position']
            driver_1_gap = arr.iloc[counter]['driver_1_gap']
            total_time_driver_1 = arr.iloc[counter]['total_time_driver_1']
            avg_laptime_driver_1 = arr.iloc[counter]['avg_laptime_driver_1']
            iqr_driver_1 = arr.iloc[counter]['iqr_driver_1']
            number_pit_driver_1 = arr.iloc[counter]['number_pit_driver_1']
            total_duration_pit_driver_1 = arr.iloc[counter]['total_duration_pit_driver_1']
            
            driver_2_name = arr.iloc[counter]['driver_2_name']
            driver_2_position = arr.iloc[counter]['driver_2_position']
            driver_2_gap = arr.iloc[counter]['driver_2_gap']
            total_time_driver_2 = arr.iloc[counter]['total_time_driver_2']
            avg_laptime_driver_2 = arr.iloc[counter]['avg_laptime_driver_2']
            iqr_driver_2 = arr.iloc[counter]['iqr_driver_2']
            number_pit_driver_2 = arr.iloc[counter]['number_pit_driver_2']
            total_duration_pit_driver_2 = arr.iloc[counter]['total_duration_pit_driver_2']
            
            fastest_driver_1 = arr.iloc[counter]['fastest_driver_1']
            fastest_driver_2 = arr.iloc[counter]['fastest_driver_2']
            safety_car_lap = arr.iloc[counter]['safety_car_lap']
            fastest_lap = arr.iloc[counter]['fastest_lap']
            
            prs.slide_width = Pt(1080)
            prs.slide_height = Pt(1350)
            blank_slide_layout = prs.slide_layouts[5]
            slide = prs.slides.add_slide(blank_slide_layout)

            #BACKGROUND
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(21, 21, 30)
            
            #TRANSPARANT LAYER
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(40), top=Pt(130), width=Pt(500), height=Pt(166))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color[0], team_color[1], team_color[2])
            _set_shape_transparency(shape,15000)
            
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(540), top=Pt(130), width=Pt(500), height=Pt(166))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color_2[0], team_color_2[1], team_color_2[2])
            _set_shape_transparency(shape,15000)
            
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(40), top=Pt(298), width=Pt(231), height=Pt(390))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color[0], team_color[1], team_color[2])
            _set_shape_transparency(shape,15000)
            
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(809), top=Pt(298), width=Pt(231), height=Pt(390))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color_2[0], team_color_2[1], team_color_2[2])
            _set_shape_transparency(shape,15000)
            
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(40), top=Pt(690), width=Pt(350), height=Pt(84))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color[0], team_color[1], team_color[2])
            _set_shape_transparency(shape,15000)
            
            shapes = slide.shapes
            shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(690), top=Pt(690), width=Pt(350), height=Pt(84))
            shape.line.fill.background()
            shapeFill = shape.fill
            shapeFill.solid()
            shapeColour = shapeFill.fore_color
            shapeColour.rgb = RGBColor(team_color_2[0], team_color_2[1], team_color_2[2])
            _set_shape_transparency(shape,15000)
            
            #HEADER
            f1_logo = '/home/kurios/Documents/f1_analysis/data/external/team_logos/F1_75_Logo.png'
            pic = slide.shapes.add_picture(f1_logo, Pt(40), Pt(54), height=Pt(32), width= Pt(200))

            title = slide.shapes.title
            title.text = race_name
            title.top = Pt(24)
            title.left = Pt(240)
            title.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
            title.text_frame.paragraphs[0].font.size = Pt(42)
            title.text_frame.paragraphs[0].font.name = 'Formula1 Display Bold'

            pic = slide.shapes.add_picture(team_logo, Pt(820), Pt(25), height= Pt(100), width=Pt(200))
            
            #STRUCTURE
            line1=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(130), Pt(1000), Pt(2))
            line1.line.fill.background()
            fill = line1.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line2=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(296), Pt(1000), Pt(2))
            line2.line.fill.background()
            fill = line2.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line3=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(688), Pt(1000), Pt(2))
            line3.line.fill.background()
            fill = line3.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line4=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(774), Pt(1000), Pt(2))
            line4.line.fill.background()
            fill = line4.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line5=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(539), Pt(130), Pt(2), Pt(166))
            line5.line.fill.background()
            fill = line5.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line6=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(390), Pt(688), Pt(2), Pt(86))
            line6.line.fill.background()
            fill = line6.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            line7=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(690), Pt(688), Pt(2), Pt(86))
            line7.line.fill.background()
            fill = line7.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(244, 244, 244)

            #TRANSPARENT FIGURES
            
            lap_counter = 0
               
            total_lap_width = 110
            fastest_lap = ast.literal_eval(fastest_lap)
            while lap_counter < len(fastest_lap):
                if fastest_lap[lap_counter] == 0:
                    team_color_graph = team_color
                elif fastest_lap[lap_counter] == 1:
                    team_color_graph = team_color_2
                else :
                    team_color_graph=[120,120,120]
                
                figure_width = 856.8
                lap_width = figure_width/len(fastest_lap)
                shapes = slide.shapes
                shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(total_lap_width), top=Pt(782), width=Pt(lap_width), height=Pt(385))
                shape.line.fill.background()
                shapeFill = shape.fill
                shapeFill.solid()
                shapeColour = shapeFill.fore_color
                shapeColour.rgb = RGBColor(team_color_graph[0], team_color_graph[1], team_color_graph[2])
                _set_shape_transparency(shape,15000)
                total_lap_width += lap_width

                lap_counter += 1
            
            #FIGURES
            pic = slide.shapes.add_picture(image_file=(figures_path+laptime_scatterplot), left=Pt(249), top=Pt(283), height=Pt(420), width=Pt(575))

            pic = slide.shapes.add_picture(image_file=(figures_path+driver_1_pace), left=Pt(19), top=Pt(284), height= Pt(390.5), width=Pt(270))

            pic = slide.shapes.add_picture(image_file=(figures_path+driver_2_pace), left=Pt(790), top= Pt(284), height= Pt(390), width=Pt(270))
            
            pic = slide.shapes.add_picture(image_file=(figures_path+laptime_comp), left=Pt(-28), top = Pt(722), height= Pt(500), width=Pt(1108))

            pic = slide.shapes.add_picture(image_file=(figures_path+tyre_strategy), left=Pt(45), top= Pt(1150),height=Pt(125), width=Pt(943))
            
            #REFERENCES
            txBox = slide.shapes.add_textbox(left=Pt(70), top= Pt(120), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Driver"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(1010), top= Pt(120), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Driver"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(104), top= Pt(205), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Avg Lap Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)

            txBox = slide.shapes.add_textbox(left=Pt(976), top= Pt(205), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Avg Lap Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(335), top= Pt(120), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Race Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)

            txBox = slide.shapes.add_textbox(left=Pt(535), top= Pt(120), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Race Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(335), top= Pt(205), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Gap"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)

            txBox = slide.shapes.add_textbox(left=Pt(535), top= Pt(205), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Gap"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(165), top= Pt(205), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "IQR"
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(16)
            run.font.bold = True
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(720), top= Pt(205), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "IQR"
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(16)
            run.font.bold = True
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(430), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Race Comparaison"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 270

            txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(500), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Race Comparaison"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 90
            
            txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(920), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Lap Time Per Lap"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 270

            txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(990), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Lap Time Per Lap"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 90
            
            txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(1210), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Tyre Strategy"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 270

            txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(1260), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Tyre Strategy"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            txBox.rotation = 90
            
            txBox = slide.shapes.add_textbox(left=Pt(130), top= Pt(680), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Lap Advantage"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(310), top= Pt(680), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Position"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(540), top= Pt(680), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Safety Car Lap"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(770), top= Pt(680), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Position"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(950), top= Pt(680), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Lap Advantage"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(200), top= Pt(1250), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Total Pit Stop Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(1250), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Pit Stops"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(650), top= Pt(1250), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Pit Stops"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)
            
            txBox = slide.shapes.add_textbox(left=Pt(880), top= Pt(1250), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Total Pit Stop Time"
            run.font.name = 'Formula1 Display Bold'
            run.font.size = Pt(16)
            p.font.color.rgb = RGBColor(120, 120, 120)        
            
            #NEUTRAL VARIABLE
                    
            txBox = slide.shapes.add_textbox(left=Pt(540), top= Pt(700), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = safety_car_lap
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            #DRIVER 1 VARIABLE

            txBox = slide.shapes.add_textbox(left=Pt(40), top=Pt(140), width=Pt(500), height=Pt(20))
            txBox.text_frame.auto_size = False
            tf = txBox.text_frame
            p = tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = name_driver_1
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(335), top= Pt(140), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = total_time_driver_1
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(115), top= Pt(225), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = avg_laptime_driver_1
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(165), top= Pt(225), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(iqr_driver_1)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
                     
            txBox = slide.shapes.add_textbox(left=Pt(335), top= Pt(225), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = driver_1_gap
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
                     
            txBox = slide.shapes.add_textbox(left=Pt(130), top= Pt(700), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = fastest_driver_1
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
                     
            txBox = slide.shapes.add_textbox(left=Pt(310), top= Pt(700), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(driver_1_position)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(200), top= Pt(1270), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = total_duration_pit_driver_1
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(1270), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(number_pit_driver_1)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            #DRIVER 2 VARIABLE
            txBox = slide.shapes.add_textbox(left=Pt(745), top= Pt(140), width=Pt(300), height=Pt(20))
            txBox.text_frame.auto_size = False
            tf = txBox.text_frame
            p = tf.add_paragraph()
            p.alignment = PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = driver_2_name
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(743), top= Pt(225), width=Pt(300), height=Pt(20))
            txBox.text_frame.auto_size = False
            tf = txBox.text_frame
            p = tf.add_paragraph()
            p.alignment = PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = avg_laptime_driver_2
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(545), top= Pt(140), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = total_time_driver_2
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(720), top= Pt(225), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(iqr_driver_2)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
                     
            txBox = slide.shapes.add_textbox(left=Pt(545), top= Pt(225), width=Pt(200), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = driver_2_gap
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
                     
            txBox = slide.shapes.add_textbox(left=Pt(770), top= Pt(700), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(driver_2_position)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)    
                 
            txBox = slide.shapes.add_textbox(left=Pt(950), top= Pt(700), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = fastest_driver_2
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(650), top= Pt(1270), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = str(number_pit_driver_2)
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
            txBox = slide.shapes.add_textbox(left=Pt(880), top= Pt(1270), width=Pt(0), height=Pt(20))
            tf = txBox.text_frame
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = total_duration_pit_driver_2
            run.font.name = 'Formula1 Display Regular'
            run.font.size = Pt(30)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            counter +=1
            
        except:
            xml_slides = prs.slides._sldIdLst  
            slides = list(xml_slides)
            xml_slides.remove(slides[counter]) 
            print(f'{team} not in {race_session_name}')
    os.chdir('/home/kurios/Documents/f1_analysis/reports/reports/test/')
    prs.save(f'{race_number}_{race_session_name}.pptx')