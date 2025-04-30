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
    driver0_name = fastf1.plotting.get_driver_name(team_drivers[0], session).split()[1].lower()
    driver1_name = fastf1.plotting.get_driver_name(team_drivers[1], session).split()[1].lower()
    if driver0_name == 'verstappen':
        driver0_name = 'max_verstappen'
    pit0 = ergast.get_pit_stops(season = year, round = race_number, driver=driver0_name).content
    pit1 = ergast.get_pit_stops(season = year, round = race_number, driver=driver1_name).content
    
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
    driver0_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver1_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver0_laps.loc[0, 'LapTime'] = driver0_laps.loc[1, 'LapStartTime'] - driver0_laps.loc[0, 'LapStartTime']
    driver1_laps.loc[0, 'LapTime'] = driver1_laps.loc[1, 'LapStartTime'] - driver1_laps.loc[0, 'LapStartTime']
    fastest_driver_per_lap = []
    if len(driver0_laps) == len(driver1_laps):
        for lap in range(len(driver0_laps)):
            if '4' in str(driver0_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver0_laps['LapTime'][lap] < driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver0_laps['LapTime'][lap] > driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
    elif len(driver0_laps) > len(driver1_laps):
        for lap in range(len(driver1_laps)):
            if '4' in str(driver0_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver0_laps['LapTime'][lap] < driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver0_laps['LapTime'][lap] > driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
        for lap in range(len(driver1_laps), len(driver0_laps)):
            if '4' in str(driver0_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            else:
                fastest_driver_per_lap.append(0)
    elif len(driver0_laps) < len(driver1_laps):
        for lap in range(len(driver0_laps)):
            if '4' in str(driver0_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            elif driver0_laps['LapTime'][lap] < driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(0)
            elif driver0_laps['LapTime'][lap] > driver1_laps['LapTime'][lap]:
                fastest_driver_per_lap.append(1)
        for lap in range(len(driver0_laps), len(driver1_laps)):
            if '4' in str(driver1_laps['TrackStatus'][lap]):
                fastest_driver_per_lap.append(2)
            else:
                fastest_driver_per_lap.append(1)
    driver0_faster = str(fastest_driver_per_lap.count(0))+ '/' + str(len(fastest_driver_per_lap))
    driver1_faster = str(fastest_driver_per_lap.count(1))+ '/' + str(len(fastest_driver_per_lap))
    safety_car_lap = str(fastest_driver_per_lap.count(2))+ '/' + str(len(fastest_driver_per_lap))

    team_info = [
        driver0_faster,
        driver1_faster,
        safety_car_lap,
        fastest_driver_per_lap
    ]
    return team_info

def get_final_gap(session, team_drivers):
    driver0_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver1_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, session.total_laps+1)).reset_index()
    driver0_laps.loc[0, 'LapTime'] = driver0_laps.loc[1, 'LapStartTime'] - driver0_laps.loc[0, 'LapStartTime']
    driver1_laps.loc[0, 'LapTime'] = driver1_laps.loc[1, 'LapStartTime'] - driver1_laps.loc[0, 'LapStartTime']
    zero_time = timedelta(0)

    if len(driver0_laps) == len(driver1_laps):
        if driver0_laps['Time'].iloc[-1] > driver1_laps['Time'].iloc[-1]:
            gap = str(driver0_laps['Time'].iloc[-1] - driver1_laps['Time'].iloc[-1])[7:]
            driver0_gap = '+' + str(gap)[3:-3]
            driver1_gap = '-' + str(gap)[3:-3]
        elif driver0_laps['Time'].iloc[-1] < driver1_laps['Time'].iloc[-1]:
            gap = str(zero_time - (driver0_laps['Time'].iloc[-1] - driver1_laps['Time'].iloc[-1]))[7:]
            driver0_gap = '-' + str(gap)[3:-3]
            driver1_gap = '+' + str(gap)[3:-3]
    elif len(driver0_laps) > len(driver1_laps):
        gap = len(driver0_laps) - len(driver1_laps)
        driver0_gap = '-' + str(gap) + ' laps'
        driver1_gap = '+' + str(gap) + ' laps'
    elif len(driver0_laps) < len(driver1_laps):
        gap = len(driver1_laps) - len(driver0_laps)
        driver0_gap = '+' + str(gap) + ' laps'
        driver1_gap = '-' + str(gap) + ' laps'
    if driver0_gap[1:4] == '00:':
        driver0_gap = driver0_gap[0] + driver0_gap[4:]
    if driver1_gap[1:4] == '00:':
        driver1_gap = driver1_gap[0] + driver1_gap[4:]
        
    return driver0_gap, driver1_gap

def get_drivers_info(session,team_drivers):
    driver0_laps = session.laps.pick_drivers(team_drivers[0]).pick_quicklaps(1.4).reset_index()
    driver1_laps = session.laps.pick_drivers(team_drivers[1]).pick_quicklaps(1.4).reset_index()
    driver0_laps.loc[0, 'LapTime'] = driver0_laps.loc[1, 'LapStartTime'] - driver0_laps.loc[0, 'LapStartTime']
    driver1_laps.loc[0, 'LapTime'] = driver1_laps.loc[1, 'LapStartTime'] - driver1_laps.loc[0, 'LapStartTime']

    driver0_name = fastf1.plotting.get_driver_name(team_drivers[0], session)
    driver1_name = fastf1.plotting.get_driver_name(team_drivers[1], session)
    if driver0_name == 'Andrea Kimi Antonelli':
        driver0_name = 'Kimi Antonelli'
    if driver1_name == 'Andrea Kimi Antonelli':
        driver1_name = 'Kimi Antonelli'
    if driver0_name == 'Oliver Bearman':
        driver0_name = 'Ollie Bearman'
    if driver1_name == 'Oliver Bearman':
        driver1_name = 'Ollie Bearman'
    
    driver0_gap, driver1_gap = get_final_gap(session, team_drivers)
    if 'Race' in row[0]:
        pit0_number, pit0_total_duration, pit1_number, pit1_total_duration = get_pitstop_time(session, team_drivers)
    elif 'Sprint' in row[0]:
        pit0_number = 0
        pit0_total_duration = timedelta(0)
        pit1_number = 0
        pit1_total_duration = timedelta(0)
    
    try :
        driver0_position = driver0_laps['Position'].iloc[-1]
    except:
        driver0_position = 'DNF'
            
    try:
        driver1_position = driver1_laps['Position'].iloc[-1]
    except:
        driver1_position = 'DNF'
        
    try:
        driver0_laps['LapTime'] = driver0_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver0 = str(driver0_laps['Time'].iloc[-1] - driver0_laps['Time'][0])[8:-3]
        driver0_avg_lap = str(timedelta(seconds = driver0_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver0_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver0_iqr = round(q3 - q1, 3)
    except:
        race_time_driver0 = 0
        driver0_avg_lap= 0
        driver0_iqr= 0
        
    try:
        driver1_laps['LapTime'] = driver1_laps['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver1 = str(driver1_laps['Time'].iloc[-1] - driver1_laps['Time'][0])[8:-3]        
        driver1_avg_lap = str(timedelta(seconds = driver1_laps['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver1_laps['LapTime'].dt.total_seconds(), [75 ,25])
        driver1_iqr = round(q3 - q1, 3)

    except:
        race_time_driver1 = 0
        driver1_avg_lap= 0
        driver1_iqr= 0
        
    drivers_info = [
        driver0_name,
        driver0_position,
        driver0_gap,
        race_time_driver0,
        driver0_avg_lap,
        driver0_iqr,
        pit0_number,
        pit0_total_duration,
        driver1_name,
        driver1_position,
        driver1_gap,
        race_time_driver1,
        driver1_avg_lap,
        driver1_iqr,
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
            if 'driver0_pace' in row[0]:
                if team in row[0]:
                    pace_comp0.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w250?authuser=0'})
            if 'driver1_pace' in row[0]:
                if team in row[0]:
                    pace_comp1.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w250?authuser=0'})

lap_info_per_team = [['EventName', 'TeamLogo', 'laptime_scatterplot', 'laptime_comp', 'tyre_strategy', 'pace_comp0', 'pace_comp1', 'driver0_name', 'driver0_position', 'driver0_gap', 'total_time_driver0', 'avg_laptime_driver0','iqr_driver0', 'pit0_number', 'pit0_total_duration', 'driver1_name', 'driver1_position', 'driver1_gap', 'total_time_driver1', 'avg_laptime_driver1','iqr_driver1', 'pit1_number', 'pit1_total_duration', 'fastest_driver0', 'fastest_driver1', 'safety_car_lap', 'gap_info_per_lap']]
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
