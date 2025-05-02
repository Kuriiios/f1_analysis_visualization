import fastf1
import fastf1.plotting
from fastf1 import utils 

import os  
import numpy as np
import pandas as pd
import csv

year = int(input("Year ? "))
race_number = int(input("Race Number ? (1-24) "))
race_session = input('Session ? (SQ, Q) ')

session = fastf1.get_session(year, race_number, race_session)
session.load()
q1, q2, q3 = session.laps.split_qualifying_sessions()

teams = fastf1.plotting.list_team_names(session)
circuit_info = session.get_circuit_info()

def show_driver_delta(team_drivers, quali_session, delta_per_team):
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()

    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None):
        delta_time, ref_tel, compare_tel = utils.delta_time(driver_1_lap, driver_2_lap)
        delta_time_at_corner = [0]
        for idx_corner, corner in circuit_info.corners.iterrows():
                for idx_dist ,dist in ref_tel['Distance'].items():
                        if dist > corner['Distance']:
                                delta_time_at_corner.append(round(delta_time[idx_dist],3))
                                break
        delta_time_at_corner.append(round(delta_time.iloc[-1],3))
        delta_time_at_corner_diff = np.diff(delta_time_at_corner).tolist()
        delta_time_at_corner_diff = [round(elem, 3) for elem in delta_time_at_corner_diff]
        delta_per_team.update({f'{sub_session}_{team}': delta_time_at_corner_diff})
        return delta_per_team

def create_csv_lap_info(quali_session, list):

    driver_info_csv = list
    event_title = event_name.split(' ', 1)[0]+ ' GP Qualifying '+sub_session
    
    v_min = 1000
    v_max = 0
    delta_by_team = delta_per_team[f'{sub_session}_{team}']
    team_info = [
        event_title,
        #delta_by_team,
        ]
    corner_advantage_driver_2 = str(len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_driver_1 = str(len(delta_by_team)-len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_team = [corner_advantage_driver_1, corner_advantage_driver_2]
    for driver in team_drivers:
        driver_lap = quali_session.pick_drivers(driver).pick_fastest()
        if type(driver_lap) != type(None):
            if team_drivers[0] in  quali_session['Driver'].values and team_drivers[1] in  quali_session['Driver'].values:

                driver_name = fastf1.plotting.get_driver_name(driver, session)
                driver_tel = driver_lap.get_car_data()
                full_throttle = round(len(np.where(driver_tel['Throttle'].values >= 90)[0])/len(driver_tel)*100)
                brake = round(len(np.where(driver_tel['Brake'] == True)[0])/len(driver_tel)*100)
                cornering = 100 - full_throttle - brake               
                v_min = int(min(v_min, min(driver_tel['Speed'])))
                v_max = int(max(v_max, max(driver_tel['Speed'])))
                driver_info = [
                    driver_name,
                    str(driver_lap['LapTime'])[10:-3],
                    str(driver_lap['Sector1Time'])[13:-3],
                    str(driver_lap['Sector2Time'])[13:-3],
                    str(driver_lap['Sector3Time'])[13:-3],
                    str(int(driver_lap['SpeedI1']))+' kp/h',
                    str(int(driver_lap['SpeedI2']))+' kp/h',
                    str(int(driver_lap['SpeedFL']))+' kp/h',
                    str(full_throttle)+'%',
                    str(brake)+'%',
                    str(cornering)+'%',
                ]
                team_info.extend(driver_info)
    gap = round(float(team_info[2][3:])-float(team_info[13][3:]), 3)
    gap1 = round(float(team_info[13][3:])-float(team_info[2][3:]), 3)
    gaps = [gap, gap1]
    team_info.extend(gaps)
    v_speed = [str(v_min)+' kp/h', str(v_max)+' kp/h']
    team_info.extend(v_speed)
    team_info.extend(corner_advantage_team)
    driver_info_csv.append(team_info)   
    return driver_info_csv

delta_per_team = {}
                    
lap_info_per_driver_q1 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q2 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q3 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]


csv_file_path_q1 = f'{race_number}_{race_session}_drivers_info_Q1.csv'
csv_file_path_q2 = f'{race_number}_{race_session}_drivers_info_Q2.csv'
csv_file_path_q3 = f'{race_number}_{race_session}_drivers_info_Q3.csv'    

event_name = session.event.EventName

for idx, team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    try:
        if team_drivers[0] in  q1['Driver'].values and team_drivers[1] in  q1['Driver'].values:
            sub_session = 'Q1'
            delta_per_team.update(show_driver_delta(team_drivers, q1, delta_per_team))
            driver_info_figma_q1 = create_csv_lap_info(q1, lap_info_per_driver_q1)

        if team_drivers[0] in  q2['Driver'].values and team_drivers[1] in  q2['Driver'].values:
            sub_session = 'Q2'
            delta_per_team.update(show_driver_delta(team_drivers, q2, delta_per_team))
            driver_info_figma_q2 = create_csv_lap_info(q2, lap_info_per_driver_q2)
            
        if team_drivers[0] in  q3['Driver'].values and team_drivers[1] in  q3['Driver'].values:
            sub_session = 'Q3'
            delta_per_team.update(show_driver_delta(team_drivers, q3, delta_per_team))
            driver_info_figma_q3 = create_csv_lap_info(q3, lap_info_per_driver_q3)
    except:
        print(f'{team} not found') 
os.chdir('/home/kurios/Documents/f1_analysis/reports/csv')
with open(csv_file_path_q1, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q1)
        
with open(csv_file_path_q2, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q2)
        
with open(csv_file_path_q3, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q3)
