import fastf1
import fastf1.plotting
import numpy as np
import pandas as pd
import data.fetch_data as dt
from datetime import timedelta

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

def microseconds_to_mmss(x, pos):
    try:
        td = timedelta(microseconds=x/1000)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02}"
    except Exception as e:
        return "0:00"

def seconds_to_mmss(x, pos):
    try:
        td = timedelta(seconds=x/1)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02}"
    except Exception as e:
        return "0:00"