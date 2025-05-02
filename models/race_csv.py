import fastf1
import fastf1.plotting

import pandas as pd
import numpy as np
import os  
from datetime import timedelta
import csv
from fastf1.ergast import Ergast

ergast = Ergast()

#year = 2025
#race_number = 1
#race_session = 'R'

year = int(input("Year ?"))
race_number = int(input("Race Number ?"))
race_session = input('Session ?')

session= fastf1.get_session(year, race_number, race_session)
session.load()

pit = ergast.get_pit_stops(season = year, round = race_number )
teams = fastf1.plotting.list_team_names(session)

def get_pitstop_time(session, team_drivers):
    driver_1_name = fastf1.plotting.get_driver_name(team_drivers[0], session).split()[1].lower()
    driver_2_name = fastf1.plotting.get_driver_name(team_drivers[1], session).split()[1].lower()
    if driver_1_name == 'verstappen':
        driver_1_name = 'max_verstappen'
    pit0 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_1_name).content
    pit1 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_2_name).content
    
    try:
        pit0_number = str(pit0[0]['stop'].iloc[-1])
        pit0_total_duration = str(pit0[0]['duration'].sum())[10:-3]
    except:
        pit0_number = 0
        pit0_total_duration = timedelta(0)
    try:
        pit1_number = str(pit1[0]['stop'].iloc[-1])
        pit1_total_duration = str(pit1[0]['duration'].sum())[10:-3]
    except:
        pit1_number = 0
        pit1_total_duration = timedelta(0)
        
    return pit0_number, pit0_total_duration, pit1_number, pit1_total_duration

def get_faster_driver_per_lap(session, team_drivers):
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
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
    driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
    zero_time = timedelta(0)

    if len(driver_1_laps) == len(driver_2_laps):
        if driver_1_laps['Time'].iloc[-1] > driver_2_laps['Time'].iloc[-1]:
            gap = str(driver_1_laps['Time'].iloc[-1] - driver_2_laps['Time'].iloc[-1])[7:]
            driver_1_gap = '+' + str(gap)[3:-3]
            driver_2_gap = '-' + str(gap)[3:-3]
        elif driver_1_laps['Time'].iloc[-1] < driver_2_laps['Time'].iloc[-1]:
            gap = str(zero_time - (driver_1_laps['Time'].iloc[-1] - driver_2_laps['Time'].iloc[-1]))[7:]
            driver_1_gap = '-' + str(gap)[3:-3]
            driver_2_gap = '+' + str(gap)[3:-3]
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
    driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
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
    if 'Race' in row[0]:
        pit0_number, pit0_total_duration, pit1_number, pit1_total_duration = get_pitstop_time(session, team_drivers)
    elif 'Sprint' in row[0]:
        pit0_number = 0
        pit0_total_duration = timedelta(0)
        pit1_number = 0
        pit1_total_duration = timedelta(0)
    
    try :
        driver_1_position = driver_1_laps['Position'].iloc[-1]
    except:
        driver_1_position = 'DNF'
            
    try:
        driver_2_position = driver_2_laps['Position'].iloc[-1]
    except:
        driver_2_position = 'DNF'
        
    try:
        driver_1_laps['LapTime'] = driver_1_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_1 = str(driver_1_laps['Time'].iloc[-1] - driver_1_laps['Time'][0])[8:-3]
        driver_1_avg_lap = str(timedelta(seconds = driver_1_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_1_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver_1_iqr = round(q3 - q1, 3)
    except:
        race_time_driver_1 = 0
        driver_1_avg_lap= 0
        driver_1_iqr= 0
        
    try:
        driver_2_laps['LapTime'] = driver_2_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_2 = str(driver_2_laps['Time'].iloc[-1] - driver_2_laps['Time'][0])[8:-3]        
        driver_2_avg_lap = str(timedelta(seconds = driver_2_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_2_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver_2_iqr = round(q3 - q1, 3)

    except:
        race_time_driver_2 = 0
        driver_2_avg_lap= 0
        driver_2_iqr= 0
        
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
    
def create_csv_race_info(session, team, list, col1, col2, col3, col4, col5, drivers_info, team_info):
    race_info_csv = list
    df_logo=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/team_logo.csv", index_col='team')
    team_logo = df_logo.iat[idx,0]
    if 'Race' in row[0]:
        event_title = session.event.EventName.split(' ', 1)[0]+ ' GP Race '
    elif 'Sprint' in row[0]:
        event_title = session.event.EventName.split(' ', 1)[0]+ ' GP Sprint Race '
    laptime_scatterplot = col1[team]
    laptime_comp = col2[team]
    tyre_strategy = col3[team]
    pace_comp0 = col4[team]
    pace_comp1 = col5[team]
    race_info = [
        event_title,
        team_logo,
        laptime_scatterplot,
        laptime_comp,
        tyre_strategy,
        pace_comp0,
        pace_comp1,
    ]
    race_info.extend(drivers_info)
    race_info.extend(team_info)
    race_info_csv.append(race_info)
    return race_info_csv
    
    
teams = fastf1.plotting.list_team_names(session)

laptime_scatterplot = {}
laptime_comp = {}
tyre_strategy = {}
pace_comp0 = {}
pace_comp1 = {}

csv_file_path = f'{race_number}_{race_session}_race_info.csv'

path = '../data/interim/'
keyword = f'{race_number}_{race_session}_drive-explorer'
for fname in os.listdir(path):
    if keyword in fname:
        driver_data = fname
os.chdir(path)
arr = np.loadtxt(driver_data, skiprows=1,
                 delimiter=',', dtype=str)

new_arr = []
for row in arr:
    new_arr.append([row[3], row[4]])

for row in new_arr:            
    if 'Race' in row[0] or 'Sprint' in row[0]:
        for team in teams:
            if 'laptime_scatterplot' in row[0]:
                if team in row[0]:
                    laptime_scatterplot.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w400?authuser=0'})
            if 'laptime_comp' in row[0]:
                if team in row[0]:
                    laptime_comp.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1100?authuser=0'})
            if 'tyre_strategy' in row[0]:
                if team in row[0]:
                    tyre_strategy.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1100?authuser=0'})
            if 'driver_1_pace' in row[0]:
                if team in row[0]:
                    pace_comp0.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w250?authuser=0'})
            if 'driver_2_pace' in row[0]:
                if team in row[0]:
                    pace_comp1.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w250?authuser=0'})

lap_info_per_team = [['EventName', 'TeamLogo', 'laptime_scatterplot', 'laptime_comp', 'tyre_strategy', 'pace_comp0', 'pace_comp1', 'driver_1_name', 'driver_1_position', 'driver_1_gap', 'total_time_driver_1', 'avg_laptime_driver_1','iqr_driver_1', 'pit0_number', 'pit0_total_duration', 'driver_2_name', 'driver_2_position', 'driver_2_gap', 'total_time_driver_2', 'avg_laptime_driver_2','iqr_driver_2', 'pit1_number', 'pit1_total_duration', 'fastest_driver_1', 'fastest_driver_2', 'safety_car_lap', 'gap_info_per_lap']]
second_color_dict = {'Red Bull Racing' :'#E30118', 'Alpine':'#2173B8', 'Mercedes':'#C8CCCE', 'Aston Martin':'#CEDC00', 'Ferrari':'#FFF200', 'Racing Bulls':'#0402C4', 'Williams':'#041E42', 'Kick Sauber':'#474f54', 'Haas F1 Team':'#E6002B', 'McLaren':'#47C7FC'}
race_info = []
for idx,team in enumerate(teams):
    try:
        team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
        drivers_info = get_drivers_info(session, team_drivers)
        team_info = get_faster_driver_per_lap(session, team_drivers)
        race_info = create_csv_race_info(session, team, lap_info_per_team, laptime_scatterplot, laptime_comp, tyre_strategy, pace_comp0, pace_comp1, drivers_info, team_info)
    except:
        print(team,'not found')
os.chdir('../../reports/csv')
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(race_info)
