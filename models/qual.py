import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
from pathlib import Path
from instagrapi import Client
import subprocess
from pdf2image import convert_from_path

import numpy as np 
import pandas as pd

from matplotlib import colormaps
from chromato.spaces import convert

import fastf1
import fastf1.plotting
from fastf1 import utils

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.enum.text import PP_ALIGN
from pptx.enum.text import MSO_AUTO_SIZE

import os
import csv

parent_file = Path(__file__).resolve().parent.parent

cache_folder = parent_file / 'cache_folder'
cache_folder.mkdir(exist_ok=True)

fastf1.Cache.enable_cache(cache_folder)

fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                          color_scheme='fastf1')

year = int(input('Year ? '))
race_number = int(input('Race Number ? (1-24) '))
race_session = input('Session ? (Q, SQ) ')
post_option = input('Do you want to post it immediatly ? (Y/N) ')

session = fastf1.get_session(year, race_number, race_session)
session.load()

q1, q2, q3 = session.laps.split_qualifying_sessions()
is_nat = np.isnat(q1['LapTime'])
q1 = q1[~is_nat]
is_nat = np.isnat(q2['LapTime'])
q2 = q2[~is_nat]
is_nat = np.isnat(q3['LapTime'])
q3 = q3[~is_nat]

if race_session == 'Q':
    race_session_name = 'Qualifying'
elif race_session == 'SQ':
    race_session_name = 'Sprint Qualifying'

event_name = session.event.EventName
figures_folder = parent_file / 'figures' / f"{race_number}_{event_name}_{session.event.year}"
report_folder = parent_file / 'reports' / f"{race_number}_{event_name}_{session.event.year}"

report_folder.mkdir(parents=True, exist_ok=True)
figures_folder.mkdir(parents=True, exist_ok=True)

circuit_info = session.get_circuit_info()
teams = fastf1.plotting.list_team_names(session)

def session_type(race_session):
    match race_session:
        case 'Q':
            return 'Qualifying'
        case 'SQ':
            return 'Sprint Qualifying'

def read_credentials(file= parent_file / "login.txt"):
    creds = {}
    with open(file) as f:
        for line in f:
            key, value = line.strip().split("=")
            creds[key] = value
    return creds

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def get_corner_dist_for_drivers(driver_tel):
    driver_corner_distance = []
    i= 0 
    for index, row in driver_tel.iterrows():
        distance = row['Distance']
        if i == len(circuit_info.corners):
            break
        elif distance > circuit_info.corners['Distance'][i]:
            driver_corner_distance.append(row)
            i+=1
    return driver_corner_distance

def add_turn(driver_tel):

    driver_distance = get_corner_dist_for_drivers(driver_tel)
    
    list_turn = []
    for i in range(len(driver_distance)):
        list_turn.append(driver_distance[i]['Distance'])
        
    turn_values = list(range(1, len(list_turn) + 1)) 
    list_turn = np.array([entry['Distance'] for entry in driver_distance])
    values = driver_tel['Distance'].values
    turn = np.zeros_like(values, dtype=int)
    for i, val in enumerate(values):
        for j in range(0, len(list_turn)): 
            if val <= list_turn[j]:
                turn[i] = turn_values[j]
                break
    return turn

def add_faster_driver(driver_tel, faster_driver, corner_distance):
    
    values = driver_tel['Turn'].values
    faster = np.zeros_like(values, dtype=int)
    for i, val in enumerate(faster_driver):
        if val == 1 :
            faster[values == i+1] = 1 
    return faster

def convert_for_cmap(base_color):
    base_color_rgb = convert.hex_to_rgb(base_color)
    r = base_color_rgb.r/255
    g = base_color_rgb.g/255
    b = base_color_rgb.b/255
    
    return r, g, b

def get_delta_per_team(team_drivers, quali_session):
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    
    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None):
        delta_time, ref_tel, compare_tel = utils.delta_time(driver_1_lap, driver_2_lap)
        max_delta = max(abs(min(delta_time)), abs(max(delta_time))) + 0.1 

    delta_time_at_corner = [0]
    for idx_corner, corner in circuit_info.corners.iterrows():
            for idx_dist ,dist in ref_tel['Distance'].items():
                    if dist > corner['Distance']:
                            delta_time_at_corner.append(round(delta_time[idx_dist],3))
                            break
    delta_time_at_corner_diff = np.diff(delta_time_at_corner).tolist()
    delta_time_at_corner_diff = [round(elem, 3) for elem in delta_time_at_corner_diff]
    delta_per_team.update({f'{subsession_name}_{team}': delta_time_at_corner_diff})
    return delta_per_team

def show_corner_advantage_per_quali_session(team_drivers, quali_session):
    gaps = [1 if gap >= 0 else 0 for gap in delta_per_team[f'{subsession_name}_{team}']]

    lap = session.laps.pick_drivers(team_drivers[0]).pick_fastest()
    tel = lap.get_telemetry()
    tel['Turn'] = add_turn(tel)
    corner_distance = circuit_info.corners['Distance']
    tel['faster_driver'] = add_faster_driver(tel, gaps, corner_distance)
    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(points, angle=track_angle)
    segments = np.concatenate([rotated_track[:-1], rotated_track[1:]], axis=1)
    first_values = [pair[0][0] for pair in rotated_track]
    second_values = [pair[0][1] for pair in rotated_track]
    
    cmap = colormaps['Paired']

    tc_r , tc_g, tc_b = convert_for_cmap(team_color) 
    tc_r2 , tc_g2, tc_b2 = convert_for_cmap(team_color_2) 

    cdict = {
        'red': (
            (0.0, 0.0, tc_r2),
            (0.0, 0.0, 0.1),
            (1.0, tc_r, 1.0),
        ),
        'green': (
            (0.0, 0.0, tc_g2),
            (0.0, 0.0, 0.0),
            (1.0, tc_g, 0.0),
        ),
        'blue': (
            (0.0, 0.0, tc_b2),
            (0.0, 0.0, 0.0),
            (1.0, tc_b, 0.0),
        )
    }

    cmap = mcolors.LinearSegmentedColormap('my_colormap', cdict)
    lc_comp = LineCollection(segments,linewidths=4, cmap=cmap)
    lc_comp.set_array(tel['faster_driver'])

    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    plt.plot(first_values, second_values,
        color='grey', linestyle='-', linewidth=8)
    plt.plot(rotated_track[0], rotated_track[1])
    offset_vector = [1000, 0] 

    offset_angle = 1 / 180 * np.pi
    offset_x, offset_y = rotate(offset_vector, angle=offset_angle)
    txt_sl ='Start / Finish Line'
    txt_sl_x = tel['X'].iloc[0] + offset_x
    txt_sl_y = tel['Y'].iloc[0] + offset_y
    txt_sl_x, txt_sl_y = rotate([txt_sl_x, txt_sl_y], angle=track_angle)
    plt.text(txt_sl_x, txt_sl_y, txt_sl,
             va='center_baseline', ha='center', size='small', weight='bold', color='white')
    
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}" 
        
        offset_angle = corner['Angle'] / 180 * np.pi
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)

        plt.text(text_x, text_y, txt,
                va='center_baseline', ha='center', size=16, weight='bold', color='white')
    
    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)
    fig.tight_layout()
    plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_corner_domination', transparent=True)

    
def create_bar_graph_per_driver(team_drivers, quali_session):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None) :
        
        driver_1_tel = driver_1_lap.get_car_data()
    
        full_throttle = round(len(np.where(driver_1_tel['Throttle'].values >= 90)[0])/len(driver_1_tel)*100)
        brake = round(len(np.where(driver_1_tel['Brake'] == True)[0])/len(driver_1_tel)*100)
        cornering = 100 - full_throttle - brake

        driver_2_tel = driver_2_lap.get_car_data()
    
        full_throttle1 = round(len(np.where(driver_2_tel['Throttle'].values >= 90)[0])/len(driver_2_tel)*100)
        brake1 = round(len(np.where(driver_2_tel['Brake'] == True)[0])/len(driver_2_tel)*100)
        cornering1 = 100 - full_throttle - brake
        
        keys=('Full Throttle','Braking', 'Cornering' )
        
        full_throttle_bar = np.array([100, full_throttle])
        brake_bar = np.array([100, brake])
        cornering_bar = np.array([100, cornering])
        plt.subplots(figsize=(5, 2))
        plt.tick_params(
            axis='both',
            which='both',
            bottom=False,
            left=False,
            labelleft=False,
            labelbottom=False)
        plt.barh(keys[2], cornering_bar, height=0.4 ,color = ['#696969', team_color])
        plt.barh(keys[1], brake_bar, height=0.4, color = ['#696969', team_color])
        plt.barh(keys[0], full_throttle_bar, height=0.4, color = ['#696969', team_color ])
        plt.rcParams['axes.spines.left'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.bottom'] = False
        plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_driver_1_bar_graph', transparent=True)

        
        full_throttle_bar1 = np.array([100, full_throttle1])
        brake_bar1 = np.array([100, brake1])
        cornering_bar1 = np.array([100, cornering1])
        plt.subplots(figsize=(5, 2))
        plt.barh(keys[2], cornering_bar1, height=0.4, color = ['#696969', team_color_2 ])
        plt.barh(keys[1], brake_bar1, height=0.4, color = ['#696969', team_color_2])
        plt.barh(keys[0], full_throttle_bar1, height=0.4, color = ['#696969', team_color_2 ])
        plt.gca().invert_xaxis()
        plt.rcParams['axes.spines.left'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.bottom'] = False
        plt.tick_params(
            axis='both',
            which='both',
            bottom=False,
            left=False,
            labelleft=False,
            labelbottom=False)
        plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_driver_2_bar_graph', transparent=True)


def show_driver_quali_dif_per_lap(team_drivers, quali_session):
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        labelleft=False,
        labelbottom=False)  
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False  
    
    fig, ax = plt.subplots(figsize=(13, 2.5))
        
    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None):
            delta_time, ref_tel, compare_tel = utils.delta_time(driver_1_lap, driver_2_lap)
            max_delta = max(abs(min(delta_time)), abs(max(delta_time))) + 0.1 
            ax.vlines(x=circuit_info.corners['Distance'], ymin=-max_delta, ymax=max_delta, colors='white', linestyle='dotted')
            plt.axhline(y=0, color= team_color_2, linewidth=3)
            ax.plot(ref_tel['Distance'], delta_time, color=team_color, linewidth=3)
    
    delta_time_at_corner = [0]
    for idx_corner, corner in circuit_info.corners.iterrows():
            for idx_dist ,dist in ref_tel['Distance'].items():
                    if dist > corner['Distance']:
                            delta_time_at_corner.append(round(delta_time[idx_dist],3))
                            break
    delta_time_at_corner.append(round(delta_time.iloc[-1],3))
    delta_time_at_corner_diff = np.diff(delta_time_at_corner).tolist()
    delta_time_at_corner_diff = [round(elem, 3) for elem in delta_time_at_corner_diff]
    delta_per_team.update({f'{subsession_name}_{team}': delta_time_at_corner_diff})
    
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        labelleft=False,
        labelbottom=False)
    plt.ylim(-max_delta, max_delta)
    plt.xlim(0, max(ref_tel['Distance']))
    
    minor_xticks = np.arange(0, max(ref_tel['Distance']), max(ref_tel['Distance'])/100)
    minor_yticks = np.arange(-max_delta, max_delta, (max_delta)/6)
    ax.set_xticks(minor_xticks, minor=True, labels=None)
    ax.set_yticks(minor_yticks, minor=True, labels=None)
    ax.grid(which='minor', alpha=0.1)
    plt.xlim(0, max(ref_tel['Distance']))
    fig.tight_layout()
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_deltatime', transparent=True)

    
def show_fastest_lap_per_quali_session(team_drivers, quali_session):
    fig, ax = plt.subplots(figsize=(13, 4.5))
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        labelleft=False,
        labelbottom=False)
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    car_data = driver_1_lap.get_car_data().add_distance()
    
    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None):
            delta_time, ref_tel, compare_tel = utils.delta_time(driver_1_lap, driver_2_lap)
    for driver in team_drivers:
        driver_lap = quali_session.pick_drivers(driver).pick_fastest()
        v_min = car_data['Speed'].min()
        v_max = car_data['Speed'].max()
                        
        if type(driver_lap) != type(None):
            
            driver_tel = driver_lap.get_car_data().add_distance()

            car_data = driver_lap.get_car_data().add_distance()
            
            for _, corner in circuit_info.corners.iterrows():
                txt = f"{corner['Number']}{corner['Letter']}"
                ax.text(corner['Distance'], v_min-(v_min*0.4), txt,
                        va='center_baseline', ha='center', size='xx-large')

            if driver == team_drivers[0] :
                ax.vlines(x=circuit_info.corners['Distance'], ymin = -v_min - 20 , ymax = v_max + 30, colors='white', linestyle='dotted')
                ax.plot(driver_tel['Distance'], driver_tel['Speed'], color=team_color, linewidth=3)
            else:
                ax.plot(driver_tel['Distance'], driver_tel['Speed'], color=team_color_2, linewidth=3)
    
    minor_xticks = np.arange(0, max(ref_tel['Distance']), max(ref_tel['Distance'])/100)
    minor_yticks = np.arange(v_min -20, v_max + 20, (v_max + 20)/30)
    ax.set_ylim([v_min - 20, v_max + 20])
    ax.set_xticks(minor_xticks, minor=True, labels=None)
    ax.set_yticks(minor_yticks, minor=True, labels=None)
    ax.grid(which='minor', alpha=0.1)
    plt.xlim(0, max(ref_tel['Distance']))
    
    fig.tight_layout()
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_speed', transparent=True)


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
    
def show_corner_segments(team_drivers, quali_session, corner_segments):
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    corner_segments_list = [0]
    if type(driver_1_lap) != type(None) and type(driver_2_lap) != type(None):
        delta_time, ref_tel, compare_tel = utils.delta_time(driver_1_lap, driver_2_lap)
        figure_diff = max(ref_tel['Distance'])/994
        for idx_corner, corner in circuit_info.corners.iterrows():
                corner_segments_list.append(corner['Distance']/figure_diff)
        figure_width = 994
        corner_segments_list.append(figure_width)
        corner_segments_diff = np.diff(corner_segments_list).tolist()
        corner_segments_diff = [elem for elem in corner_segments_diff]
        corner_segments.update({f'{sub_session}_{team}': corner_segments_diff})

        return corner_segments

def create_csv_lap_info(quali_session, list):

    driver_info_csv = list
    if race_session == 'Q':
        event_title = event_name.split(' ', 1)[0]+ ' GP Qualifying '+sub_session
    elif race_session == 'SQ':
        event_title = event_name.split(' ', 1)[0]+ ' GP Sprint Quali '+sub_session
    
    v_min = 1000
    v_max = 0
    delta_by_team = delta_per_team[f'{sub_session}_{team}']
    team_info = [
        event_title,
        ]
    corner_advantage_driver_2 = str(len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_driver_1 = str(len(delta_by_team)-len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >=0]))+'/'+str(len(delta_by_team))
    corner_advantage_team = [corner_advantage_driver_1, corner_advantage_driver_2]
    for driver in team_drivers:
        driver_lap = quali_session.pick_drivers(driver).pick_fastest()
        if type(driver_lap) != type(None):
            if team_drivers[0] in  quali_session['Driver'].values and team_drivers[1] in  quali_session['Driver'].values:
                driver_name = fastf1.plotting.get_driver_name(driver, session)
                if driver_name == 'Andrea Kimi Antonelli':
                    driver_name = 'Kimi Antonelli'
                elif driver_name == 'Oliver Bearman':
                    driver_name = 'Ollie Bearman'
                driver_tel = driver_lap.get_car_data()
                full_throttle = round(len(np.where(driver_tel['Throttle'].values >= 90)[0])/len(driver_tel)*100)
                brake = round(len(np.where(driver_tel['Brake'] == True)[0])/len(driver_tel)*100)
                cornering = 100 - full_throttle - brake
                v_min = int(min(v_min, min(driver_tel['Speed'])))
                v_max = int(max(v_max, max(driver_tel['Speed'])))
                
                try:
                    SpeedI1 = str(int(driver_lap['SpeedI1']))+' kp/h'
                except :
                    SpeedI1 = 'No data'

                if len(str(driver_lap['LapTime'])) == 15:
                    laptime = str(driver_lap['LapTime'])[10:]+'.000'
                else:
                    laptime = str(driver_lap['LapTime'])[10:-3]
                    
                driver_info = [
                    driver_name,
                    laptime,
                    str(driver_lap['Sector1Time'])[13:-3],
                    str(driver_lap['Sector2Time'])[13:-3],
                    str(driver_lap['Sector3Time'])[13:-3],
                    SpeedI1,
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

def SubElement(parent, tagname, **kwargs):
        element = OxmlElement(tagname)
        element.attrib.update(kwargs)
        parent.append(element)
        return element

def _set_shape_transparency(shape, alpha):
    ts = shape.fill._xPr.solidFill
    sF = ts.get_or_change_to_srgbClr()
    sE = SubElement(sF, 'a:alpha', val=str(alpha))
    
def Hex_RGB(ip):
    return tuple(int(ip[i+1:i+3],16) for i in (0, 2, 4))

delta_per_team = {}
for subsession in [q1, q2, q3]:
    if subsession is q1:
        subsession_name = 'Q1'
    elif subsession is q2:
        subsession_name = 'Q2'
    elif subsession is q3:
        subsession_name = 'Q3'
    for idx, team in enumerate(teams):
        team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
        team_color = fastf1.plotting.get_team_color(team, session=session)
        df_color=pd.read_csv(parent_file / "data/raw/second_color.csv", index_col='team')
        team_color_2 = df_color.iat[idx,0]
        try:
            delta_per_team = get_delta_per_team(team_drivers, subsession)
            show_driver_quali_dif_per_lap(team_drivers, subsession)
            show_fastest_lap_per_quali_session(team_drivers, subsession)
            show_corner_advantage_per_quali_session(team_drivers=team_drivers, quali_session = subsession)
            create_bar_graph_per_driver(team_drivers, subsession)
        except:
            print(f'No data in {subsession_name} for {team}')

delta_per_team = {}
corner_segments = {}
                    
lap_info_per_driver_q1 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q2 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]
lap_info_per_driver_q3 = [['EventName', 'Name','LapTime', 'Sector1', 'Sector2', 'Sector3', 'SpeedTrap1', 'SpeedTrap2', 'SpeedFL', 'FullThrottle', 'Brake', 'Cornering', 'Name_1','LapTime_1', 'Sector1_1', 'Sector2_1', 'Sector3_1', 'SpeedTrap1_1', 'SpeedTrap2_1', 'SpeedFL_1', 'FullThrottle_1', 'Brake_1', 'Cornering_1', 'Gap', 'Gap1', 'V_min', 'V_max', 'corner_advantage', 'corner_advantage1']]

csv_file_path_q1 = f'{race_number}_{race_session}_drivers_info_Q1.csv'
csv_file_path_q2 = f'{race_number}_{race_session}_drivers_info_Q2.csv'
csv_file_path_q3 = f'{race_number}_{race_session}_drivers_info_Q3.csv'   

csv_file_path_delta_per_team = f'{race_number}_{race_session}_drivers_info_delta_per_team.csv'   
csv_file_path_corner_segments = f'{race_number}_{race_session}_drivers_info_corner_segments.csv'   
 

event_name = session.event.EventName

for idx, team in enumerate(teams):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    try:
        if team_drivers[0] in  q1['Driver'].values and team_drivers[1] in  q1['Driver'].values:
            sub_session = 'Q1'
            delta_per_team.update(show_driver_delta(team_drivers, q1, delta_per_team))
            corner_segments.update(show_corner_segments(team_drivers, q1,corner_segments))
            driver_info_figma_q1 = create_csv_lap_info(q1, lap_info_per_driver_q1)

        if team_drivers[0] in  q2['Driver'].values and team_drivers[1] in  q2['Driver'].values:
            sub_session = 'Q2'
            delta_per_team.update(show_driver_delta(team_drivers, q2, delta_per_team))
            corner_segments.update(show_corner_segments(team_drivers, q2,corner_segments))
            driver_info_figma_q2 = create_csv_lap_info(q2, lap_info_per_driver_q2)
            
        if team_drivers[0] in  q3['Driver'].values and team_drivers[1] in  q3['Driver'].values:
            sub_session = 'Q3'
            delta_per_team.update(show_driver_delta(team_drivers, q3, delta_per_team))
            corner_segments.update(show_corner_segments(team_drivers, q3,corner_segments))
            driver_info_figma_q3 = create_csv_lap_info(q3, lap_info_per_driver_q3)
    except:
        print(f'{team} not found') 
os.chdir(parent_file / 'csv')
with open(csv_file_path_q1, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q1)
        
with open(csv_file_path_q2, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q2)
        
with open(csv_file_path_q3, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(driver_info_figma_q3)
        
df_delta_per_team = pd.DataFrame(delta_per_team)
df_delta_per_team.to_csv(csv_file_path_delta_per_team, index=False)
        
df_corner_segments = pd.DataFrame(corner_segments)
df_corner_segments.to_csv(csv_file_path_corner_segments, index=False)

path = parent_file / 'csv/'

for subsession in [q1, q2, q3]:
    prs = Presentation()
    if subsession is q1:
        subsession_name = 'Q1'
    elif subsession is q2:
        subsession_name = 'Q2'
    elif subsession is q3:
        subsession_name = 'Q3'
    keyword = f'{race_number}_{race_session}_drivers_info_{subsession_name}'
    for fname in os.listdir(path):
        if keyword in fname:
            driver_data = fname
    os.chdir(path)
    arr = np.loadtxt(driver_data, skiprows=1,
                    delimiter=',', dtype=str)
    keyword = f'{race_number}_{race_session}_drivers_info_corner_segments'
    for fname in os.listdir(path):
        if keyword in fname:
            driver_data = fname
    os.chdir(path)
    corner_segments_arr = np.loadtxt(driver_data, skiprows=1,
                    delimiter=',', dtype=str)
    
    keyword = f'{race_number}_{race_session}_drivers_info_delta_per_teams'
    for fname in os.listdir(path):
        if keyword in fname:
            driver_data = fname
    os.chdir(path)
    delta_per_teams_arr = np.loadtxt(driver_data, skiprows=1,
                    delimiter=',', dtype=str)
    subsession = subsession.drop(subsession[subsession.Deleted == True].index)
    counter = 0
    for idx, team in enumerate(teams):
        team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
        team_color = fastf1.plotting.get_team_color(team, session=session)
        df_color=pd.read_csv(parent_file / "data/raw/second_color.csv", index_col='team')
        team_color_2 = df_color.iat[idx,0]
        team_color = Hex_RGB(team_color)
        team_color_2 = Hex_RGB(team_color_2)
        
        if team_drivers[0] in  subsession['Driver'].values and team_drivers[1] in  subsession['Driver'].values:
            try:
                race_name = arr[counter][0]
                team_logo = parent_file / f'data/external/team_logos/{team}.png'
                corner_domination = figures_folder / f'{subsession_name}_{team}_corner_domination.png'
                delta_time = figures_folder / f'{subsession_name}_{team}_deltatime.png'
                speed = figures_folder / f'{subsession_name}_{team}_speed.png'
                
                name_driver_1 = arr[counter][1]
                lap_time_driver_1 = arr[counter][2]
                sector_1_driver_1 = arr[counter][3]
                sector_2_driver_1 = arr[counter][4]
                sector_3_driver_1 = arr[counter][5]
                speed_trap_1_driver_1 = arr[counter][6]
                speed_trap_2_driver_1 = arr[counter][7]
                speed_final_line_driver_1 = arr[counter][8]
                gap_driver_1 = arr[counter][23]
                corner_advantage_driver_1 = arr[counter][27
                                                    ]
                throttling_driver_1 = arr[counter][9]
                braking_driver_1 = arr[counter][10]
                cornering_driver_1 = arr[counter][11]
                bar_graph_driver_1 =  figures_folder / f'{subsession_name}_{team}_driver_1_bar_graph.png'

                name_driver_2 = arr[counter][12]
                lap_time_driver_2 = arr[counter][13]
                sector_1_driver_2 = arr[counter][14]
                sector_2_driver_2 = arr[counter][15]
                sector_3_driver_2 = arr[counter][16]
                speed_trap_1_driver_2 = arr[counter][17]
                speed_trap_2_driver_2 = arr[counter][18]
                speed_final_line_driver_2 = arr[counter][19]
                gap_driver_2 = arr[counter][24]
                corner_advantage_driver_2 = arr[counter][28]
                throttling_driver_2 = arr[counter][20]
                braking_driver_2 = arr[counter][21]
                cornering_driver_2 = arr[counter][22]
                bar_graph_driver_2 = figures_folder / f'{subsession_name}_{team}_driver_2_bar_graph.png'
                
                v_min = arr[counter][-4]
                v_max = arr[counter][-3]
                
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
                shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(40), top=Pt(130), width=Pt(300), height=Pt(435))
                shape.line.fill.background()
                shapeFill = shape.fill
                shapeFill.solid()
                shapeColour = shapeFill.fore_color
                shapeColour.rgb = RGBColor(team_color[0], team_color[1], team_color[2])
                _set_shape_transparency(shape,15000)
                
                shapes = slide.shapes
                shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(340), top=Pt(385), width=Pt(200), height=Pt(180))
                shape.line.fill.background()
                shapeFill = shape.fill
                shapeFill.solid()
                shapeColour = shapeFill.fore_color
                shapeColour.rgb = RGBColor(team_color[0], team_color[1], team_color[2])
                _set_shape_transparency(shape,15000)
                
                shapes = slide.shapes
                shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(740), top=Pt(130), width=Pt(300), height=Pt(435))
                shape.line.fill.background()
                shapeFill = shape.fill
                shapeFill.solid()
                shapeColour = shapeFill.fore_color
                shapeColour.rgb = RGBColor(team_color_2[0], team_color_2[1], team_color_2[2])
                _set_shape_transparency(shape,15000)
                
                shapes = slide.shapes
                shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(540), top=Pt(385), width=Pt(200), height=Pt(180))
                shape.line.fill.background()
                shapeFill = shape.fill
                shapeFill.solid()
                shapeColour = shapeFill.fore_color
                shapeColour.rgb = RGBColor(team_color_2[0], team_color_2[1], team_color_2[2])
                _set_shape_transparency(shape,15000)
                
                #HEADER
                f1_logo = parent_file / 'data/external/team_logos/F1_75_Logo.png'
                pic = slide.shapes.add_picture(str(f1_logo), Pt(40), Pt(54), height=Pt(32), width= Pt(200))

                title = slide.shapes.title
                title.text = race_name
                title.top = Pt(24)
                title.left = Pt(195)

                title.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
                title.text_frame.paragraphs[0].font.size = Pt(38)
                title.text_frame.paragraphs[0].font.name = 'Formula1 Display Bold'

                pic = slide.shapes.add_picture(str(team_logo), Pt(820), Pt(25), height= Pt(100), width=Pt(200))
                
                #STRUCTURE
                line1=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(130), Pt(1000), Pt(2))
                line1.line.fill.background()
                fill = line1.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(244, 244, 244)

                line2=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(565), Pt(1000), Pt(2))
                line2.line.fill.background()
                fill = line2.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(244, 244, 244)

                line3=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(785), Pt(1000), Pt(2))
                line3.line.fill.background()
                fill = line3.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(244, 244, 244)

                line4=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(539), Pt(590), Pt(2), Pt(180))
                line4.line.fill.background()
                fill = line4.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(244, 244, 244)

                line5=slide.shapes.add_shape(MSO_CONNECTOR.STRAIGHT, Pt(539), Pt(385), Pt(2), Pt(180))
                line5.line.fill.background()
                fill = line5.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(244, 244, 244)

                #TRANSPARENT FIGURES
                transparent_counter = 0
                df_delta = pd.read_csv(parent_file / f'csv/{race_number}_{race_session}_drivers_info_delta_per_team.csv')
                df_delta_columns = list(df_delta.columns)
                delta_index = df_delta_columns.index(f'{subsession_name}_{team}')
                
                df_corner = pd.read_csv(parent_file / f'csv/{race_number}_{race_session}_drivers_info_corner_segments.csv')
                df_corner_columns = list(df_corner.columns)
                corner_index = df_corner_columns.index(f'{subsession_name}_{team}')
        
                total_lenght_corner_segments = 44
                while transparent_counter < len(df_delta):
                    if df_delta.iloc[transparent_counter, delta_index] > 0:
                        team_color_graph = team_color
                    else:
                        team_color_graph = team_color_2
                    lenght_corner_segments = df_corner.iloc[transparent_counter, corner_index]
                    
                    shapes = slide.shapes
                    shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(total_lenght_corner_segments), top=Pt(810), width=Pt(lenght_corner_segments), height=Pt(305))
                    shape.line.fill.background()
                    shapeFill = shape.fill
                    shapeFill.solid()
                    shapeColour = shapeFill.fore_color
                    shapeColour.rgb = RGBColor(team_color_graph[0], team_color_graph[1], team_color_graph[2])
                    _set_shape_transparency(shape,15000)
                    
                    shapes2 = slide.shapes
                    shape2 = shapes2.add_shape(MSO_SHAPE.RECTANGLE, left=Pt(total_lenght_corner_segments), top=Pt(1150), width=Pt(lenght_corner_segments), height=Pt(175))
                    shape2.line.fill.background()
                    shape2Fill = shape2.fill
                    shape2Fill.solid()
                    shape2Colour = shape2Fill.fore_color
                    shape2Colour.rgb = RGBColor(team_color_graph[0], team_color_graph[1], team_color_graph[2])
                    _set_shape_transparency(shape2,15000)
                    total_lenght_corner_segments += lenght_corner_segments

                    transparent_counter += 1

                #FIGURES
                pic = slide.shapes.add_picture(image_file=(str(corner_domination)), left=Pt(342), top = Pt(75), height= Pt(395), width=Pt(395))

                pic = slide.shapes.add_picture(image_file=(str(bar_graph_driver_1)), left=Pt(0), top=Pt(565), height= Pt(228), width=Pt(543))

                pic = slide.shapes.add_picture(image_file=(str(bar_graph_driver_2)), left=Pt(523), top= Pt(565), height= Pt(228), width=Pt(543))

                pic = slide.shapes.add_picture(image_file=(str(delta_time)), left=Pt(30), top=Pt(1140), height=Pt(195), width=Pt(1018))

                pic = slide.shapes.add_picture(image_file=(str(speed)), left=Pt(30), top= Pt(798),height=Pt(355), width=Pt(1018))

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

                txBox = slide.shapes.add_textbox(left=Pt(85), top= Pt(205), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Lap Time"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(995), top= Pt(205), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Lap Time"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(290), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 1"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(290), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 1"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 2"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 2"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 3"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Sector 3"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(290), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Trap 1"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(290), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Trap 1"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Trap 2"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Trap 2"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Final Line"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Speed Final Line"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Gap"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(640), top= Pt(375), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Gap"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Corner Advantage"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(640), top= Pt(460), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "Corner Advantage"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(646), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "%LAP TIME"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 270

                txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(685), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "%LAP TIME"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 90

                txBox = slide.shapes.add_textbox(left=Pt(140), top= Pt(550), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "FULL THROTTLE"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(940), top= Pt(550), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "FULL THROTTLE"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(145), top= Pt(615), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "HEAVY BREAKING"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(940), top= Pt(615), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "HEAVY BREAKING"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(120), top= Pt(685), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "CORNERING"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(960), top= Pt(685), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "CORNERING"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)

                txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(935), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "SPEED"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 270

                txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(960), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "SPEED"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 90

                txBox = slide.shapes.add_textbox(left=Pt(0), top= Pt(1195), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "DELTA TIME"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 270

                txBox = slide.shapes.add_textbox(left=Pt(1080), top= Pt(1235), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = "DELTA TIME"
                run.font.name = 'Formula1 Display Bold'
                run.font.size = Pt(16)
                p.font.color.rgb = RGBColor(120, 120, 120)
                txBox.rotation = 90

                #DRIVER 1 VARIABLE

                txBox = slide.shapes.add_textbox(left=Pt(40), top=Pt(140), width=Pt(500), height=Pt(20))
                txBox.text_frame.auto_size = MSO_AUTO_SIZE.NONE
                tf = txBox.text_frame
                p = tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                run = p.add_run()
                run.text = name_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                
                txBox = slide.shapes.add_textbox(left=Pt(125), top= Pt(225), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = lap_time_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(310), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_1_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_2_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)  
                    
                txBox = slide.shapes.add_textbox(left=Pt(103), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_3_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)  
                
                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(310), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_trap_1_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_trap_2_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(260), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_final_line_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = gap_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(430), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = corner_advantage_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(500), top= Pt(572), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = throttling_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) 
                
                txBox = slide.shapes.add_textbox(left=Pt(500), top= Pt(640), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = braking_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                
                txBox = slide.shapes.add_textbox(left=Pt(500), top= Pt(705), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = cornering_driver_1
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                
                #DRIVER 2 VARIABLE
                txBox = slide.shapes.add_textbox(left=Pt(745), top= Pt(140), width=Pt(300), height=Pt(20))
                txBox.text_frame.auto_size = MSO_AUTO_SIZE.NONE
                tf = txBox.text_frame
                p = tf.add_paragraph()
                p.alignment = PP_ALIGN.RIGHT
                run = p.add_run()
                run.text = name_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(950), top= Pt(225), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = lap_time_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(310), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_1_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_2_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(975), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = sector_3_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(310), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_trap_1_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_trap_2_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(817), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = speed_final_line_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(640), top= Pt(395), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = gap_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(640), top= Pt(480), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = corner_advantage_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(30)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(580), top= Pt(572), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = throttling_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(580), top= Pt(640), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = braking_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

                txBox = slide.shapes.add_textbox(left=Pt(580), top= Pt(705), width=Pt(0), height=Pt(20))
                tf = txBox.text_frame
                p = tf.add_paragraph()
                run = p.add_run()
                run.text = cornering_driver_2
                run.font.name = 'Formula1 Display Regular'
                run.font.size = Pt(24)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                counter +=1
            except:
                xml_slides = prs.slides._sldIdLst  
                slides = list(xml_slides)
                xml_slides.remove(slides[counter]) 
                print(f'{team} not in {subsession_name}')
    prs.save(parent_file/ report_folder / f'{race_number}_{subsession_name}_{race_session_name}.pptx')

for file_path in report_folder.iterdir():
    if file_path.is_file() and file_path.suffix.lower() == '.pptx':
        os.chdir(report_folder)

        subprocess.run(
            [
                "/usr/bin/lowriter",
                "--headless",
                "--convert-to",
                "pdf",
                str(file_path.resolve())
            ],
            check=True
        )
        no_suffix_path = file_path.with_suffix('')
        no_suffix_path.mkdir(parents=True, exist_ok=True)
        file_path_pdf = file_path.with_suffix('.pdf')
        
        os.chdir(no_suffix_path)
        images = convert_from_path(file_path_pdf, dpi=72)
       
        for i in range(len(images)):
            images[i].save(file_path.stem + str(i) +'.jpeg', 'JPEG')
        file_path.unlink()
        file_path_pdf.unlink()


caption =  ( f"🇦🇺 Round {session.event.RoundNumber} - {session.event.EventName} ({session.event.Country})\n"
            f"📍 {session.event.Location}\n"
            f"🏁 {session_type(race_session)} Session Recap\n"
            f"———\n"
            f"Stay tuned for full weekend coverage of the {session.event.OfficialEventName}!\n"
            f"#F1 #Formula1 #F1{session.event.RoundNumber} #F1{session.event.Country.replace(' ', '')} #F1Weekend #F1Quali #F1Race #F1Team")

if post_option == 'Y':
    creds = read_credentials()
    cl = Client()
    cl.login(creds['username'], creds['password'])

    for i in range(3):
        image_folder = parent_file / f"reports/{session.event.RoundNumber}_{session.event.EventName}_{year}/{session.event.RoundNumber}_Q{str(i+1)}_{session_type(race_session)}"
        image_files = []
        for report in os.listdir(image_folder):
            image_files.append(os.path.join(image_folder, report))

        cl.album_upload(
            paths=image_files,
            caption=caption
            )
        cl.delay_range = [1, 3]