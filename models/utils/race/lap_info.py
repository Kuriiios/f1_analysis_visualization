import pandas as pd
from datetime import timedelta
import fastf1
import fastf1.plotting
from fastf1.ergast import Ergast
import numpy as np

ergast = Ergast()

def fixed_nat_all_laps(team, session):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    try:
        driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()
    except:
        driver_1_laps = pd.DataFrame()
    try:
        driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()
    except:
        driver_2_laps = pd.DataFrame()
    if not driver_1_laps.empty:
        laptime_counter_driver_1 = 0
        for lap in driver_1_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_1_laps.loc[laptime_counter_driver_1, 'LapTime'] = driver_1_laps.loc[laptime_counter_driver_1 +1, 'LapStartTime'] - driver_1_laps.loc[laptime_counter_driver_1, 'LapStartTime']
                laptime_counter_driver_1 +=1
            except KeyError:
                break

    if not driver_2_laps.empty:
        laptime_counter_driver_2 = 0
        for lap in driver_2_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_2_laps.loc[laptime_counter_driver_2, 'LapTime'] = driver_2_laps.loc[laptime_counter_driver_2 +1, 'LapStartTime'] - driver_2_laps.loc[laptime_counter_driver_2, 'LapStartTime']
                laptime_counter_driver_2 +=1
            except KeyError:
                break
    return driver_1_laps, driver_2_laps

def fixed_nat_fast_laps(team, session):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    try:
        driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_quicklaps(1.17).reset_index()
    except:
        driver_1_laps = pd.DataFrame()
    try:
        driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_quicklaps(1.17).reset_index()
    except:
        driver_2_laps = pd.DataFrame()
    if not driver_1_laps.empty:
        laptime_counter_driver_1 = 0
        for lap in driver_1_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_1_laps.loc[laptime_counter_driver_1, 'LapTime'] = driver_1_laps.loc[laptime_counter_driver_1 +1, 'LapStartTime'] - driver_1_laps.loc[laptime_counter_driver_1, 'LapStartTime']
                laptime_counter_driver_1 +=1
            except KeyError:
                break

    if not driver_2_laps.empty:
        laptime_counter_driver_2 = 0
        for lap in driver_2_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_2_laps.loc[laptime_counter_driver_2, 'LapTime'] = driver_2_laps.loc[laptime_counter_driver_2 +1, 'LapStartTime'] - driver_2_laps.loc[laptime_counter_driver_2, 'LapStartTime']
                laptime_counter_driver_2 +=1
            except KeyError:
                break
    return driver_1_laps, driver_2_laps


def get_pitstop_time(session, team_drivers, year, race_number):
    try:
        driver_1_name = fastf1.plotting.get_driver_name(team_drivers[0], session).split()[1].lower()
        if driver_1_name == 'verstappen':
            driver_1_name = 'max_verstappen'
        pit0 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_1_name).content
    except:
        driver_1_name = 'No Data'
    try:
        driver_2_name = fastf1.plotting.get_driver_name(team_drivers[1], session).split()[1].lower()
        pit1 = ergast.get_pit_stops(season = year, round = race_number, driver=driver_2_name).content
    except:
        driver_2_name = 'No Data'
    try:
        pit0_number = str(pit0[0]['stop'].iloc[-1])
        pit0_total_duration = str(pit0[0]['duration'].sum())[10:-3]+ ' s'
    except:
        pit0_number = '0'
        pit0_total_duration = '0:00.000 s'
    try:
        pit1_number = str(pit1[0]['stop'].iloc[-1])
        pit1_total_duration = str(pit1[0]['duration'].sum())[10:-3]+ ' s'
    except:
        pit1_number = '0'
        pit1_total_duration = '0:00.000 s'
        
    return pit0_number, pit0_total_duration, pit1_number, pit1_total_duration

def get_faster_driver_per_lap(session, team, team_drivers):
    driver_1_laps, driver_2_laps = fixed_nat_all_laps(team, session)

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

def get_final_gap(session, team):
    try:
        driver_1_laps, driver_2_laps = fixed_nat_all_laps(team, session)
        race_time_driver_1 = driver_1_laps['LapTime'].sum()
        race_time_driver_2 = driver_2_laps['LapTime'].sum()
        zero_time = timedelta(0)
        if len(driver_1_laps) == len(driver_2_laps):
            if race_time_driver_1 > race_time_driver_2:
                gap = str(round((pd.to_timedelta(race_time_driver_1 - race_time_driver_2).total_seconds()), 3))
                driver_1_gap = '+' + gap + ' s'
                driver_2_gap = '-' + gap + ' s'
            elif race_time_driver_1 < race_time_driver_2:
                gap = str(round((pd.to_timedelta(zero_time - (race_time_driver_1 - race_time_driver_2)).total_seconds()), 3))
                driver_1_gap = '-' + gap + ' s'
                driver_2_gap = '+' + gap + ' s'
                
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
    except:
        driver_1_gap = 'No Data'
        driver_2_gap = 'No Data'
    return driver_1_gap, driver_2_gap

def get_drivers_info(session, team, team_drivers, race_session, year, race_number):
    driver_1_laps_fast, driver_2_laps_fast = fixed_nat_fast_laps(team, session)
    driver_1_laps_all, driver_2_laps_all = fixed_nat_all_laps(team, session)
    try:
        driver_1_name = fastf1.plotting.get_driver_name(team_drivers[0], session)
    except:
        driver_1_name = 'No data'
    try:
        driver_2_name = fastf1.plotting.get_driver_name(team_drivers[1], session)
    except:
        driver_2_name = 'No data'
    if driver_1_name == 'Andrea Kimi Antonelli':
        driver_1_name = 'Kimi Antonelli'
    if driver_2_name == 'Andrea Kimi Antonelli':
        driver_2_name = 'Kimi Antonelli'
    if driver_1_name == 'Oliver Bearman':
        driver_1_name = 'Ollie Bearman'
    if driver_2_name == 'Oliver Bearman':
        driver_2_name = 'Ollie Bearman'
    
    driver_1_gap, driver_2_gap = get_final_gap(session, team)
  
    if race_session == 'R':
        pit0_number, pit0_total_duration, pit1_number, pit1_total_duration = get_pitstop_time(session, team_drivers, year, race_number)
    elif race_session == 'S':
        pit0_number = 0
        pit0_total_duration = timedelta(0)
        pit1_number = '0'
        pit1_total_duration = timedelta(0)
    
    try :
        driver_1_position = int(driver_1_laps_all['Position'].iloc[-1])
    except:
        driver_1_position = 'DNF'

    try:
        driver_2_position = int(driver_2_laps_all['Position'].iloc[-1])
    except:
        driver_2_position = 'DNF'
        
    try:
        driver_1_laps_all['LapTime'] = driver_1_laps_all['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_1 = str(driver_1_laps_all['LapTime'].sum())[10:-3]
        driver_1_avg_lap = str(timedelta(seconds = driver_1_laps_fast['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_1_laps_fast['LapTime'].dt.total_seconds(), [75 ,25])
        driver_1_iqr = str(round(q3 - q1, 3))+ ' s'
    except:
        race_time_driver_1 = '0:00.000'
        driver_1_avg_lap= '0:00.000'
        driver_1_iqr= '0.000 s'
        
    try:
        driver_2_laps_all['LapTime'] = driver_2_laps_all['LapTime'].replace(pd.NaT, timedelta(0))
        race_time_driver_2 = str(driver_2_laps_all['LapTime'].sum())[10:-3]
        driver_2_avg_lap = str(timedelta(seconds = driver_2_laps_fast['LapTime'].dt.total_seconds().median()))[3:-3]
        q3, q1 = np.percentile(driver_2_laps_fast['LapTime'].dt.total_seconds(), [75 ,25])
        driver_2_iqr = str(round(q3 - q1, 3))+ ' s'

    except:
        race_time_driver_2 = '0:00:00.000'
        driver_2_avg_lap= '0:00.000'
        driver_2_iqr= '0.000 s'

    if round(q3 - q1, 3) == float(0):
        driver_2_iqr= '0.000 s'
        
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
    
def create_csv_race_info(list, drivers_info, team_info, event_name, race_session):
   
    race_info_csv = list
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
