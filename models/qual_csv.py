import fastf1
import fastf1.plotting
from fastf1 import utils 

import os  
import numpy as np
import pandas as pd
import csv

year = int(input("Year ?"))
race_number = int(input("Race Number ?"))
race_session = input('Session ?')

session = fastf1.get_session(year, race_number, race_session)
session.load()
q1, q2, q3 = session.laps.split_qualifying_sessions()

teams = fastf1.plotting.list_team_names(session)
circuit_info = session.get_circuit_info()

def show_driver_delta(team_drivers, quali_session, delta_per_team):
    driver0_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver1_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()

    if type(driver0_lap) != type(None) and type(driver1_lap) != type(None):
        delta_time, ref_tel, compare_tel = utils.delta_time(driver0_lap, driver1_lap)
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

def create_csv_lap_info(quali_session, list, col1, col2, col3, col4, col5):

    driver_info_csv = list
    df_logo=pd.read_csv("/home/kurios/Documents/f1_analysis/data/raw/team_logo.csv", index_col='team')
    team_logo = df_logo.iat[idx,0]
    corner_domination = col1[team]
    delta_time = col2[team]
    speed = col3[team]
    event_title = event_name.split(' ', 1)[0]+ ' GP Qualiying '+sub_session
    
    v_min = 1000
    v_max = 0
    delta_by_team = delta_per_team[f'{sub_session}_{team}']
    team_info = [
        event_title,
        team_logo,
        corner_domination,
        delta_time,
        speed,
        delta_by_team,
        ]
    corner_advantage_driver_1 = str(len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_driver_0 = str(len(delta_by_team)-len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_team = [corner_advantage_driver_0, corner_advantage_driver_1]
    for driver in team_drivers:
        driver_lap = quali_session.pick_drivers(driver).pick_fastest()
        if type(driver_lap) != type(None):
            if team_drivers[0] in  quali_session['Driver'].values and team_drivers[1] in  quali_session['Driver'].values:

                driver_name = fastf1.plotting.get_driver_name(driver, session)
                driver_tel = driver_lap.get_car_data()
            
                full_throttle = round(len(np.where(driver_tel['Throttle'].values >= 90)[0])/len(driver_tel)*100)
                brake = round(len(np.where(driver_tel['Brake'] == True)[0])/len(driver_tel)*100)
                cornering = 100 - full_throttle - brake
                if driver == team_drivers[0]:
                    bar_graph= col4[team]
                elif driver == team_drivers[1]:
                    bar_graph= col5[team]
                
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
                    bar_graph
                ]
                team_info.extend(driver_info)
    gap = float(team_info[7][3:])-float(team_info[19][3:])
    gap1 = float(team_info[19][3:])-float(team_info[7][3:])
    gaps = [gap, gap1]
    team_info.extend(gaps)
    v_speed = [str(v_min)+' kp/h', str(v_max)+' kp/h']
    team_info.extend(v_speed)
    team_info.extend(corner_advantage_team)
    driver_info_csv.append(team_info)   
    return driver_info_csv

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

q1_timings_corner_domination = {}
q1_timings_deltatime = {}
q1_timings_speed = {}
q1_bar_graph_driver0 = {}
q1_bar_graph_driver1 = {}

q2_timings_corner_domination = {}
q2_timings_deltatime = {}
q2_timings_speed = {}
q2_bar_graph_driver0 = {}
q2_bar_graph_driver1 = {}


q3_timings_corner_domination = {}
q3_timings_deltatime = {}
q3_timings_speed = {}
q3_bar_graph_driver0 = {}
q3_bar_graph_driver1 = {}

delta_per_team = {}

for row in new_arr:
    if 'Q1' in row[0]:
        for team in teams:
            if 'driver0_bar_graph' in row[0]:
                if team in row[0]:
                    q1_bar_graph_driver0.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'driver1_bar_graph' in row[0]:
                if team in row[0]:
                    q1_bar_graph_driver1.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'corner_domination' in row[0]:
                if team in row[0]:
                    q1_timings_corner_domination.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w400?authuser=0'})
            elif 'deltatime' in row[0]:
                if team in row[0]:
                    q1_timings_deltatime.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
            elif 'speed' in row[0]:
                if team in row[0]:
                    q1_timings_speed.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
    if 'Q2' in row[0]:
        for team in teams:
            if 'driver0_bar_graph' in row[0]:
                if team in row[0]:
                    q2_bar_graph_driver0.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'driver1_bar_graph' in row[0]:
                if team in row[0]:
                    q2_bar_graph_driver1.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'corner_domination' in row[0]:
                if team in row[0]:
                    q2_timings_corner_domination.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w400?authuser=0'})
            elif 'deltatime' in row[0]:
                if team in row[0]:
                    q2_timings_deltatime.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
            elif 'speed' in row[0]:
                if team in row[0]:
                    q2_timings_speed.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
    if 'Q3' in row[0]:
        for team in teams:
            if 'driver0_bar_graph' in row[0]:
                if team in row[0]:
                    q3_bar_graph_driver0.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'driver1_bar_graph' in row[0]:
                if team in row[0]:
                    q3_bar_graph_driver1.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w500?authuser=0'})
            if 'corner_domination' in row[0]:
                if team in row[0]:
                    q3_timings_corner_domination.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w400?authuser=0'})
            elif 'deltatime' in row[0]:
                if team in row[0]:
                    q3_timings_deltatime.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
            elif 'speed' in row[0]:
                if team in row[0]:
                    q3_timings_speed.update({f'{team}':'https://lh3.googleusercontent.com/d/'+row[1][32:65]+'=w1300?authuser=0'})
                    
lap_info_per_driver_q1 = [['EventName', 'TeamLogo', 'corner_domination', 'delta_time', 'speed', 'delta_by_team', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'bar_graph', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'bar_graph_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q2 = [['EventName', 'TeamLogo', 'corner_domination', 'delta_time', 'speed', 'delta_by_team', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'bar_graph', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'bar_graph_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q3 = [['EventName', 'TeamLogo', 'corner_domination', 'delta_time', 'speed', 'delta_by_team', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'bar_graph', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'bar_graph_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]


csv_file_path_q1 = f'{race_number}_{race_session}_drivers_info_q1.csv'
csv_file_path_q2 = f'{race_number}_{race_session}_drivers_info_q2.csv'
csv_file_path_q3 = f'{race_number}_{race_session}_drivers_info_q3.csv'    

event_name = session.event.EventName

for idx, team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    try:
        if team_drivers[0] in  q1['Driver'].values and team_drivers[1] in  q1['Driver'].values:
            sub_session = 'Q1'
            delta_per_team.update(show_driver_delta(team_drivers, q1, delta_per_team))
            driver_info_figma_q1 = create_csv_lap_info(q1, lap_info_per_driver_q1, q1_timings_corner_domination, q1_timings_deltatime, q1_timings_speed, q1_bar_graph_driver0, q1_bar_graph_driver1)

        if team_drivers[0] in  q2['Driver'].values and team_drivers[1] in  q2['Driver'].values:
            sub_session = 'Q2'
            delta_per_team.update(show_driver_delta(team_drivers, q2, delta_per_team))
            driver_info_figma_q2 = create_csv_lap_info(q2, lap_info_per_driver_q2, q2_timings_corner_domination, q2_timings_deltatime, q2_timings_speed, q2_bar_graph_driver0, q2_bar_graph_driver1)
            
        if team_drivers[0] in  q3['Driver'].values and team_drivers[1] in  q3['Driver'].values:
            sub_session = 'Q3'
            delta_per_team.update(show_driver_delta(team_drivers, q3, delta_per_team))
            driver_info_figma_q3 = create_csv_lap_info(q3, lap_info_per_driver_q3, q3_timings_corner_domination, q3_timings_deltatime, q3_timings_speed, q3_bar_graph_driver0, q3_bar_graph_driver1)
    except:
        print(f'{team} not found') 
os.chdir('../../reports/csv')
with open(csv_file_path_q1, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q1)
        
with open(csv_file_path_q2, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q2)
        
with open(csv_file_path_q3, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q3)
