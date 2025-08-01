import fastf1
import fastf1.api
import fastf1.plotting

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta

import streamlit as st
import altair as alt 

import pandas as pd

from pathlib import Path
parent_file = Path(__file__).resolve().parent.parent
save_folder_transcription = '/data_dashboard/'
save_path = str(parent_file) + save_folder_transcription

st.set_page_config(
    page_title='F1 Analysis',
    page_icon='🏁🏎️',
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.theme.enable("dark")

with st.sidebar:
    st.title('🏁🏎️ F1 Analysis')
    
    year_list = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    year = st.selectbox('Select a year', year_list, index=len(year_list)-1)

    race_list = list(range(1,25))
    race_number = st.selectbox('Select a race', race_list, index=12)

    race_session = 'Race'
    session= fastf1.get_session(year, race_number, race_session)
    session.load()
    if session.event.EventFormat == 'conventional':
        session_list = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race']
        race_session = st.selectbox('Select a session', session_list, index=len(session_list)-1)
        session= fastf1.get_session(year, race_number, race_session)
        session.load()
    elif session.event.EventFormat == 'sprint_qualifying':
        session_list = ['Practice 1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']
        race_session = st.selectbox('Select a session', session_list, index=len(session_list)-1)    
        session= fastf1.get_session(year, race_number, race_session)
        session.load()

    max_lap = int(max(session.laps.LapNumber))+1
    
    if race_session == 'Race' or race_session == 'Sprint':
        lap_list = list(range(1, max_lap))
        Lap_Number = st.selectbox('Select a lap', lap_list, index=len(lap_list)-1)
    elif race_session == 'Qualifying' or race_session == 'Sprint Qualifying':
        q1, q2, q3 = session.laps.split_qualifying_sessions()
        is_nat = np.isnat(q1['LapTime'])
        q1 = q1[~is_nat]
        is_nat = np.isnat(q2['LapTime'])
        q2 = q2[~is_nat]
        is_nat = np.isnat(q3['LapTime'])
        q3 = q3[~is_nat]

        Lap_Number = 10
           
        quali_list = ['Q1', 'Q2', 'Q3']
        quali = st.selectbox('Select a quali session', quali_list, index=0)

        minute_list = list(range(0, 61))
        minute = st.selectbox('Select a minute', minute_list, index=10)
    elif race_session == 'Practice 1' or race_session == 'Practice 2' or race_session == 'Practice 3':
        Lap_Number = 10
        minute_list = list(range(0, 61))
        minute = st.selectbox('Select a minute', minute_list, index=len(minute_list)-1)

    teams = fastf1.plotting.list_team_names(session)
    team = st.selectbox('Select a team', teams, index=4)

def highlight(s, min_max):
    if min_max == 'min':
        is_min_max = s == s.min()
    if min_max == 'max':
        is_min_max = s == s.max()

    return ['color: green' if v else 'color: orange' for v in is_min_max]

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def background_color_df(s):
    colors= []
    for time_and_compound in s:
        if 'SOFT' in time_and_compound:
            colors.append('background-color:red')
        elif 'MEDIUM' in time_and_compound:
            colors.append('background-color:yellow')
        elif 'HARD' in time_and_compound:
            colors.append('background-color:white')
        elif 'INTERMEDIATE' in time_and_compound:
            colors.append('background-color:green')
        elif 'WET' in time_and_compound:
            colors.append('background-color:blue')
        elif ' SUPERSOFT' in time_and_compound:
            colors.append('background-color:purple')
        elif ' ULTRASOFT' in time_and_compound:
            colors.append('background-color:orangered')
        elif ' HYPERSOFT' in time_and_compound:
            colors.append('background-color:pink')
        elif ' SUPERHARD' in time_and_compound:
            colors.append('background-color:orange')
        else:
            colors.append('background-color:grey')
    return colors

def fastest_per_driver(s, driver_fastest_lap):
    colors = []
    for time in s:
        if time.split(' ')[0] == overall_fastest:
            colors.append('color:purple')
        elif time.split(' ')[0] == driver_fastest_lap:
            colors.append('color:darkgreen')
        else:
            colors.append('color:black')
    return colors

def highlight_driver(s):
    drivers = []
    for driver_name in s:
        driver_color = fastf1.plotting.get_driver_color(driver_name[0:3], session)
        drivers.append(f'color: {driver_color}')
    return drivers

def color_df(s, color):
    colors= []
    for driver_name in s:
        colors.append(f'color:{color}')
    return colors

def is_personal_best_min(s, column):
    best_colors = []
    min_values = {}
    driver_ids = list(session.drivers)

    for driver_id in driver_ids:
        min_values[driver_id] = session.laps.pick_drivers(driver_id).pick_laps(range(0, Lap_Number + 1))[column].min()

    all_driver_laps = session.laps.pick_drivers(session.drivers).pick_laps(range(0, Lap_Number + 1))
    if not all_driver_laps.empty:
        overall_min = all_driver_laps[column].min()
    else:
        overall_min = 'inf'

    for column_value in s:
        color = 'color:orange'
        for driver in session.drivers:
            if column_value  == overall_min:
                color = 'color:purple'
            if column_value == min_values.get(driver):
                color = 'color:green'

        best_colors.append(color)

    return best_colors

def is_personal_best_max(s, column):
    best_colors = []
    max_values = {}
    driver_ids = list(session.drivers)

    for driver_id in driver_ids:
        max_values[driver_id] = session.laps.pick_drivers(driver_id).pick_laps(range(0, Lap_Number + 1))[column].max()

    all_driver_laps = session.laps.pick_drivers(session.drivers).pick_laps(range(0, Lap_Number + 1))
    if not all_driver_laps.empty:
        overall_max = all_driver_laps[column].max()
    else:
        overall_max = 0
    
    for column_value in s:
        color = 'color:orange'
        for driver in session.drivers:
            if column_value == overall_max:
                color = 'color:purple'
            elif column_value == max_values.get(driver):
                color = 'color:green'

        best_colors.append(color)

    return best_colors

def flag_color_row(s):
    flag_colors=[]
    for flag_color in s:
        match flag_color:
            case flag_color if 'GREEN' in flag_color:
                flag_colors.append('color:green')
            case flag_color if 'YELLOW' in flag_color:
                flag_colors.append('color:yellow')
            case flag_color if 'DOUBLE YELLOW' in flag_color:
                flag_colors.append('color:orange')
            case flag_color if 'RED' in flag_color:
                flag_colors.append('color:red')
            case flag_color if 'BLUE' in flag_color:
                flag_colors.append('color:blue')
            case flag_color if 'CLEAR' in flag_color:
                flag_colors.append('color:white')
            case flag_color if 'BLACK' in flag_color:
                flag_colors.append('color:dark-grey')
            case _:
                flag_colors.append('color:grey')
    return flag_colors

def get_wind_direction_cat(WindDirection):
    normalized_direction = WindDirection % 360
    if normalized_direction < 0:
        normalized_direction += 360
    match normalized_direction:
        case _ if (normalized_direction >= 348.75 or normalized_direction < 11.25):
            return 'N'
        case _ if (normalized_direction >= 11.25 and normalized_direction < 33.75):
            return 'NNE'
        case _ if (normalized_direction >= 33.75 and normalized_direction < 56.25):
            return 'NE'
        case _ if (normalized_direction >= 56.25 and normalized_direction < 78.75):
            return 'ENE'
        case _ if (normalized_direction >= 78.75 and normalized_direction < 101.25):
            return 'E'
        case _ if (normalized_direction >= 101.25 and normalized_direction < 123.75):
            return 'ESE'
        case _ if (normalized_direction >= 123.75 and normalized_direction < 146.25):
            return 'SE'
        case _ if (normalized_direction >= 146.25 and normalized_direction < 168.75):
            return 'SSE'
        case _ if (normalized_direction >= 168.75 and normalized_direction < 191.25):
            return 'S'
        case _ if (normalized_direction >= 191.25 and normalized_direction < 213.75):
            return 'SSW'
        case _ if (normalized_direction >= 213.75 and normalized_direction < 236.25):
            return 'SW'
        case _ if (normalized_direction >= 236.25 and normalized_direction < 258.75):
            return 'WSW'
        case _ if (normalized_direction >= 258.75 and normalized_direction < 281.25):
            return 'W'
        case _ if (normalized_direction >= 281.25 and normalized_direction < 303.75):
            return 'WNW'
        case _ if (normalized_direction >= 303.75 and normalized_direction < 326.25):
            return 'NW'
        case _ if (normalized_direction >= 326.25 and normalized_direction < 348.75):
            return 'NNW'
        case _:
            return 'Invalid'

tyres={
    'SOFT':'🔴',
    'MEDIUM':'🟡',
    'HARD':'⚪',
    'INTERMEDIATE':'🟢',
    'WET':'🔵',
    'SUPERSOFT': '🟣',
    'ULTRASOFT': '🟠',
    'HYPERSOFT': '🩷',
    'SUPERHARD': '🍊',
}

session= fastf1.get_session(year, race_number, race_session)
session.load()

teams = fastf1.plotting.list_team_names(session)
team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
event_name = session.event.EventName

col_row_1 = st.columns((3, 0.5, 2, 2), gap='small')
col_row_2 = st.columns((1.6, 1.6 , 4), gap='small')
col_row_3 = st.columns((1.5, 1, 1, 1 ,1 , 1.2), gap='small', vertical_alignment='center')

with col_row_1[1]:
    on_track = []
    on_track_df = []
    on_track_logo = []
    driver_names = []
    each_lap = session.laps.pick_laps(range(0, Lap_Number))
    first_driver_session_time_in_microsec = int(str((each_lap.LapStartTime[each_lap.Position == 1 & (each_lap.LapNumber == max(each_lap.LapNumber))].values/1000)[0]).split(' ')[0])

    for driver in session.drivers:

        each_lap = session.laps.pick_laps(range(0, Lap_Number)).pick_drivers(driver)
        each_lap = each_lap[each_lap.Position == each_lap.Position]
        try:
            each_lap_data = each_lap.get_pos_data()
            on_track.append('On Track')
            on_track_logo.append('🟢')
        except:
            on_track.append('DNF')
            on_track_logo.append('🔴')
    on_track_df = pd.DataFrame({
        'Status':on_track,
        'PU':on_track_logo}, index = session.drivers)
    st.dataframe(on_track_df) 

with col_row_1[2]:
    driver_data_last_laps = []
    driver_data_cols = ['Time', 'Lap', 'Sector1', 'I1', 'Sector2', 'I2', 'Sector3', 'FL', 'LapTime', 'ST']
    driver = team_drivers[1]
    driver_lap = session.laps.pick_drivers(driver)
    max_lap = int(max(driver_lap.LapNumber))

    if Lap_Number<10:
        lap_range =range(0, min(Lap_Number, max_lap))
    else :
        lap_range = range(min(Lap_Number-10, max_lap - 10), min(Lap_Number, max_lap))
    
    for lap in lap_range:
        try:
            driver_color = fastf1.plotting.get_driver_color(driver_lap.Driver.iloc[lap], session)
            driver_data = [driver_lap.Time.iloc[lap], driver_lap.LapNumber.iloc[lap], driver_lap.Sector1Time.iloc[lap], driver_lap.SpeedI1.iloc[lap], driver_lap.Sector2Time.iloc[lap], driver_lap.SpeedI2.iloc[lap], driver_lap.Sector3Time.iloc[lap], driver_lap.SpeedFL.iloc[lap], driver_lap.LapTime.iloc[lap], driver_lap.SpeedST.iloc[lap]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_last_laps.append(driver_data_series)

    driver_data_last_laps_df = pd.DataFrame(driver_data_last_laps)
    styled_df = driver_data_last_laps_df.style

    styled_df = styled_df.apply(highlight, subset=['Sector1'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['I1'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['Sector2'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['I2'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['Sector3'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['FL'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['LapTime'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['ST'], min_max='max')

    formatters = {
        'Time': lambda x: str(x)[7:-3] if pd.notnull(x) else 'Ø',
        'Lap': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'I1': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'I2': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'FL': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'Ø',
        'ST': lambda x: int(x) if pd.notnull(x) else 'Ø',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_last_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, hide_index=True)

with col_row_1[3]:
    driver_data_last_laps = []

    driver_data_cols = ['Time', 'Lap', 'Sector1', 'I1', 'Sector2', 'I2', 'Sector3', 'FL', 'LapTime', 'ST']
    driver = team_drivers[1]
    driver_lap = session.laps.pick_drivers(driver)
    max_lap = int(max(driver_lap.LapNumber))

    if Lap_Number<10:
        lap_range =range(0, min(Lap_Number, max_lap))
    else :
        lap_range = range(min(Lap_Number-10, max_lap - 10), min(Lap_Number, max_lap))
    
    for lap in lap_range:
        try:
            driver_color = fastf1.plotting.get_driver_color(driver_lap.Driver.iloc[lap], session)
            driver_data = [driver_lap.Time.iloc[lap], driver_lap.LapNumber.iloc[lap], driver_lap.Sector1Time.iloc[lap], driver_lap.SpeedI1.iloc[lap], driver_lap.Sector2Time.iloc[lap], driver_lap.SpeedI2.iloc[lap], driver_lap.Sector3Time.iloc[lap], driver_lap.SpeedFL.iloc[lap], driver_lap.LapTime.iloc[lap], driver_lap.SpeedST.iloc[lap]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_last_laps.append(driver_data_series)

    driver_data_last_laps_df = pd.DataFrame(driver_data_last_laps)
    styled_df = driver_data_last_laps_df.style
    
    styled_df = styled_df.apply(highlight, subset=['Sector1'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['I1'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['Sector2'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['I2'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['Sector3'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['FL'], min_max='max')
    styled_df = styled_df.apply(highlight, subset=['LapTime'], min_max='min')
    styled_df = styled_df.apply(highlight, subset=['ST'], min_max='max')

    formatters = {
        'Time': lambda x: str(x)[7:-3] if pd.notnull(x) else 'Ø',
        'Lap': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'I1': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'I2': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'Ø',
        'FL': lambda x: int(x) if pd.notnull(x) else 'Ø',
        'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'Ø',
        'ST': lambda x: int(x) if pd.notnull(x) else 'Ø',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_last_laps_df.columns}
    styled_df = styled_df.format(final_formatters)

    st.dataframe(styled_df, hide_index=True)

with col_row_1[0]:
    if race_session == 'Race' or race_session == 'Sprint':
        drivers_data = []
        driver_data_cols = [
            'Position', 'Driver', 'Time',
            'Gap_ahead_Driver', 'Gap_to_Leader',
            'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
            'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
        ]

        leader_driver_number = None
        leader_lap_time_reference = None
        leader_snapshot_lap_data = None

        laps_at_snapshot = session.laps[session.laps['LapNumber'] == Lap_Number]

        if not laps_at_snapshot.empty:
            leader_snapshot_lap_data = laps_at_snapshot.sort_values(by='Position').iloc[0]
            leader_driver_number = leader_snapshot_lap_data['DriverNumber']
            leader_lap_time_reference = leader_snapshot_lap_data['Time']
            try:
                leader_data = [
                    leader_snapshot_lap_data.Position, leader_snapshot_lap_data.Driver  + ' ❚ ' + leader_driver_number,
                    leader_snapshot_lap_data.Time, 0, 0, leader_snapshot_lap_data.Sector1Time, leader_snapshot_lap_data.SpeedI1,
                    leader_snapshot_lap_data.Sector2Time, leader_snapshot_lap_data.SpeedI2, leader_snapshot_lap_data.Sector3Time,
                    leader_snapshot_lap_data.SpeedFL, leader_snapshot_lap_data.LapTime, leader_snapshot_lap_data.SpeedST,
                    leader_snapshot_lap_data.LapNumber, leader_snapshot_lap_data.Compound, (leader_snapshot_lap_data.Stint - 1)
                ]
                drivers_data.append(pd.Series(leader_data, index=driver_data_cols))
            except Exception as e:
                print(f"Could not process leader's data for Lap {Lap_Number}. Error: {e}")
                exit()
        else:
            print(f"No data available for Lap {Lap_Number} to determine the leader. Cannot proceed.")
            exit()


        for driver_num in session.drivers:
            if driver_num == leader_driver_number:
                continue

            driver_laps = session.laps.pick_drivers(driver_num)
            potential_laps_after_leader = driver_laps[(driver_laps['Time'] >= leader_lap_time_reference)].copy()
            selected_lap = None
            if not potential_laps_after_leader.empty:
                selected_lap = potential_laps_after_leader.sort_values(by='LapNumber').iloc[0]
            else:
                fallback_lap = driver_laps[driver_laps['LapNumber'] == Lap_Number]
                if not fallback_lap.empty:
                    selected_lap = fallback_lap.iloc[0]
                else:
                    if not driver_laps.empty:
                        selected_lap = driver_laps.iloc[-1]
                    else:
                        continue

            if selected_lap is not None and not selected_lap.empty:
                try:
                    driver_data = [
                        selected_lap.Position, selected_lap.Driver + ' ❚ ' + driver_num,
                        selected_lap.Time, 0, 0, selected_lap.Sector1Time, selected_lap.SpeedI1,
                        selected_lap.Sector2Time, selected_lap.SpeedI2, selected_lap.Sector3Time,
                        selected_lap.SpeedFL, selected_lap.LapTime, selected_lap.SpeedST,
                        selected_lap.LapNumber, selected_lap.Compound, (selected_lap.Stint - 1)
                    ]
                    drivers_data.append(pd.Series(driver_data, index=driver_data_cols))
                except Exception as e:
                    continue

        drivers_data_df = pd.DataFrame(drivers_data)

        if drivers_data_df.empty:
            print(f"No driver data collected for this scenario. Check session data and logic.")
        else:
            drivers_data_df = drivers_data_df.fillna(0).infer_objects(copy=False)
            drivers_data_df = drivers_data_df.sort_values('Position').reset_index(drop=True)
            drivers_data_df['Tyre'] = drivers_data_df.Tyre.replace(to_replace=tyres)

            drivers_data_df['Time_td'] = drivers_data_df['Time']
            drivers_data_df['Gap_ahead_Driver'] = drivers_data_df['Time_td'].diff()
            drivers_data_df['Gap_to_Leader'] = drivers_data_df['Time_td'] - drivers_data_df['Time_td'].iloc[0]

            drivers_data_df = drivers_data_df[drivers_data_df['Position']>0]
            drivers_data_df = drivers_data_df.drop(columns=['Position', 'Time_td'])
            
            drivers_data_df.index = range(1, len(drivers_data_df) +1 )   


            styled_df = drivers_data_df.style
            styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector1'], column = 'Sector1Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector2'], column = 'Sector2Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector3'], column = 'Sector3Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['LapTime'], column = 'LapTime')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I1'], column = 'SpeedI1')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I2'], column = 'SpeedI2')
            styled_df = styled_df.apply(is_personal_best_max, subset=['FL'], column = 'SpeedFL')
            styled_df = styled_df.apply(is_personal_best_max, subset=['ST'], column = 'SpeedST')
            styled_df = styled_df.apply(color_df, subset=['Gap_ahead_Driver'], color ='orange')
            styled_df = styled_df.apply(color_df, subset=['Gap_to_Leader'], color ='orange')

            formatters = {
            'Time': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
            'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I1': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I2': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'FL': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
            'ST': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Lap': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'PitStop': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Gap_ahead_Driver': lambda x: str(abs(x))[7:-3] if pd.notnull(x) else 'No Data',
            'Gap_to_Leader': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
            }

            final_formatters = {k: v for k, v in formatters.items() if k in drivers_data_df.columns}
            styled_df = styled_df.format(final_formatters)
    elif race_session == 'Qualifying' or race_session == 'Sprint Qualifying':
        if quali == 'Q1':
            drivers_data = []
            driver_data_cols = [
                'Driver', 'Time',
                'Gap_ahead_Driver', 'Gap_to_Leader',
                'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
                'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
            ]
            fastest_lap_drivers = []
            for driver in session.drivers:
                fastest_lap_per_driver = q1.pick_drivers(driver).pick_fastest()
                try:
                    if not fastest_lap_per_driver.empty:
                        fastest_lap_per_driver = [
                            fastest_lap_per_driver.Driver  + ' ❚ ' + fastest_lap_per_driver.DriverNumber,
                            fastest_lap_per_driver.Time, 0, 0, fastest_lap_per_driver.Sector1Time, fastest_lap_per_driver.SpeedI1,
                            fastest_lap_per_driver.Sector2Time, fastest_lap_per_driver.SpeedI2, fastest_lap_per_driver.Sector3Time,
                            fastest_lap_per_driver.SpeedFL, fastest_lap_per_driver.LapTime, fastest_lap_per_driver.SpeedST,
                            fastest_lap_per_driver.LapNumber, fastest_lap_per_driver.Compound, (fastest_lap_per_driver.Stint - 1)
                        ]
                except:
                    continue
                fastest_lap_drivers.append(pd.Series(fastest_lap_per_driver, index=driver_data_cols))
            
        if quali == 'Q2':
            drivers_data = []
            driver_data_cols = [
                'Driver', 'Time',
                'Gap_ahead_Driver', 'Gap_to_Leader',
                'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
                'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
            ]
            fastest_lap_drivers = []
            for driver in session.drivers:
                fastest_lap_per_driver = q2.pick_drivers(driver).pick_fastest()
                try:
                    if not fastest_lap_per_driver.empty:
                        fastest_lap_per_driver = [
                            fastest_lap_per_driver.Driver  + ' ❚ ' + fastest_lap_per_driver.DriverNumber,
                            fastest_lap_per_driver.Time, 0, 0, fastest_lap_per_driver.Sector1Time, fastest_lap_per_driver.SpeedI1,
                            fastest_lap_per_driver.Sector2Time, fastest_lap_per_driver.SpeedI2, fastest_lap_per_driver.Sector3Time,
                            fastest_lap_per_driver.SpeedFL, fastest_lap_per_driver.LapTime, fastest_lap_per_driver.SpeedST,
                            fastest_lap_per_driver.LapNumber, fastest_lap_per_driver.Compound, (fastest_lap_per_driver.Stint - 1)
                        ]
                except:
                    continue
                fastest_lap_drivers.append(pd.Series(fastest_lap_per_driver, index=driver_data_cols))

        if quali == 'Q3':
            drivers_data = []
            driver_data_cols = [
                'Driver', 'Time',
                'Gap_ahead_Driver', 'Gap_to_Leader',
                'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
                'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
            ]
            fastest_lap_drivers = []
            for driver in session.drivers:
                fastest_lap_per_driver = q3.pick_drivers(driver).pick_fastest()
                try:
                    if not fastest_lap_per_driver.empty:
                        fastest_lap_per_driver = [
                            fastest_lap_per_driver.Driver  + ' ❚ ' + fastest_lap_per_driver.DriverNumber,
                            fastest_lap_per_driver.Time, 0, 0, fastest_lap_per_driver.Sector1Time, fastest_lap_per_driver.SpeedI1,
                            fastest_lap_per_driver.Sector2Time, fastest_lap_per_driver.SpeedI2, fastest_lap_per_driver.Sector3Time,
                            fastest_lap_per_driver.SpeedFL, fastest_lap_per_driver.LapTime, fastest_lap_per_driver.SpeedST,
                            fastest_lap_per_driver.LapNumber, fastest_lap_per_driver.Compound, (fastest_lap_per_driver.Stint - 1)
                        ]
                except:
                    continue
                fastest_lap_drivers.append(pd.Series(fastest_lap_per_driver, index=driver_data_cols))
  

        fastest_laps = pd.DataFrame(fastest_lap_drivers)
        fastest_laps['Tyre'] = fastest_laps.Tyre.replace(to_replace=tyres)
        fastest_laps = fastest_laps.sort_values(['LapTime'])
        fastest_laps['Gap_ahead_Driver'] = fastest_laps['LapTime'].diff()
        fastest_laps['Gap_to_Leader'] = fastest_laps['LapTime'] - fastest_laps['LapTime'].iloc[0]
        fastest_laps.index = range(1, len(fastest_laps) +1 )

        if fastest_laps.empty:
            print(f"No driver data collected for this scenario. Check session data and logic.")
        else:
            styled_df = fastest_laps.style
            styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector1'], column = 'Sector1Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector2'], column = 'Sector2Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector3'], column = 'Sector3Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['LapTime'], column = 'LapTime')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I1'], column = 'SpeedI1')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I2'], column = 'SpeedI2')
            styled_df = styled_df.apply(is_personal_best_max, subset=['FL'], column = 'SpeedFL')
            styled_df = styled_df.apply(is_personal_best_max, subset=['ST'], column = 'SpeedST')
            styled_df = styled_df.apply(color_df, subset=['Gap_ahead_Driver'], color ='orange')
            styled_df = styled_df.apply(color_df, subset=['Gap_to_Leader'], color ='orange')

            formatters = {
            
            'Time': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
            'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I1': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I2': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'FL': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
            'ST': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Lap': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'PitStop': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Gap_ahead_Driver': lambda x: str(abs(x))[14:-3] if pd.notnull(x) else 'No Data',
            'Gap_to_Leader': lambda x: str(x)[14:-3] if pd.notnull(x) else 'No Data',
            }

            final_formatters = {k: v for k, v in formatters.items() if k in fastest_laps.columns}
            styled_df = styled_df.format(final_formatters)
    elif race_session == 'Practice 1' or race_session == 'Practice 2' or race_session == 'Practice 3':
        drivers_data = []
        driver_data_cols = [
            'Driver', 'Time',
            'Gap_ahead_Driver', 'Gap_to_Leader',
            'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
            'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
        ]
        fastest_lap_drivers = []
        for driver in session.drivers:
            fastest_lap_per_driver = session.laps.pick_drivers(driver).pick_fastest()
            try:
                if not fastest_lap_per_driver.empty:
                    fastest_lap_per_driver = [
                        fastest_lap_per_driver.Driver  + ' ❚ ' + fastest_lap_per_driver.DriverNumber,
                        fastest_lap_per_driver.Time, 0, 0, fastest_lap_per_driver.Sector1Time, fastest_lap_per_driver.SpeedI1,
                        fastest_lap_per_driver.Sector2Time, fastest_lap_per_driver.SpeedI2, fastest_lap_per_driver.Sector3Time,
                        fastest_lap_per_driver.SpeedFL, fastest_lap_per_driver.LapTime, fastest_lap_per_driver.SpeedST,
                        fastest_lap_per_driver.LapNumber, fastest_lap_per_driver.Compound, (fastest_lap_per_driver.Stint - 1)
                    ]
            except:
                continue
            fastest_lap_drivers.append(pd.Series(fastest_lap_per_driver, index=driver_data_cols))
            fastest_laps = pd.DataFrame(fastest_lap_drivers)
            
            fastest_laps['Tyre'] = fastest_laps.Tyre.replace(to_replace=tyres)
            fastest_laps = fastest_laps.sort_values(['LapTime'])
            fastest_laps['Gap_ahead_Driver'] = fastest_laps['LapTime'].diff()
            fastest_laps['Gap_to_Leader'] = fastest_laps['LapTime'] - fastest_laps['LapTime'].iloc[0]
            fastest_laps.index = range(1, len(fastest_laps) +1 )

        if fastest_laps.empty:
            print(f"No driver data collected for this scenario. Check session data and logic.")
        else:
            styled_df = fastest_laps.style
            styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector1'], column = 'Sector1Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector2'], column = 'Sector2Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['Sector3'], column = 'Sector3Time')
            styled_df = styled_df.apply(is_personal_best_min, subset=['LapTime'], column = 'LapTime')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I1'], column = 'SpeedI1')
            styled_df = styled_df.apply(is_personal_best_max, subset=['I2'], column = 'SpeedI2')
            styled_df = styled_df.apply(is_personal_best_max, subset=['FL'], column = 'SpeedFL')
            styled_df = styled_df.apply(is_personal_best_max, subset=['ST'], column = 'SpeedST')
            styled_df = styled_df.apply(color_df, subset=['Gap_ahead_Driver'], color ='orange')
            styled_df = styled_df.apply(color_df, subset=['Gap_to_Leader'], color ='orange')

            formatters = {
            
            'Time': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
            'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I1': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'I2': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
            'FL': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
            'ST': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Lap': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'PitStop': lambda x: int(x) if pd.notnull(x) else 'No Data',
            'Gap_ahead_Driver': lambda x: str(abs(x))[14:-3] if pd.notnull(x) else 'No Data',
            'Gap_to_Leader': lambda x: str(x)[14:-3] if pd.notnull(x) else 'No Data',
            }

            final_formatters = {k: v for k, v in formatters.items() if k in fastest_laps.columns}
            styled_df = styled_df.format(final_formatters)

    st.dataframe(styled_df)

with col_row_2[0]:
    new_df = pd.read_csv(filepath_or_buffer = (str(save_path) + str(session.event.Session5Date)[:10]+'_'+str(session.event.EventName).replace(' ','_')+'.csv'), index_col=0)
    st.dataframe(new_df)

with col_row_2[1]:
    first_driver_first_lap = session.laps.pick_drivers(session.drivers).pick_laps(1)
    first_driver = session.laps.pick_drivers(session.drivers).pick_laps(Lap_Number)
    first_driver = first_driver[first_driver['Position'] == 1]
    weather_driver_lap = session.laps.get_weather_data()
    weather_driver_lap = weather_driver_lap.drop_duplicates()
    weather_driver_lap = weather_driver_lap.sort_values(['Time'])
    weather_driver_lap['Direction'] = weather_driver_lap['WindDirection'].apply(get_wind_direction_cat)
    weather_driver_lap['Time_sec'] = weather_driver_lap.Time.dt.total_seconds()
    weather_evolution = [weather_driver_lap.iloc[0],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*2],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*3],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*4],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*5],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*6],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*7],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)/9)*8],
                    weather_driver_lap.iloc[int(len(weather_driver_lap)-1)]]
    weather_evolution_df = pd.DataFrame(weather_evolution)
    weather_evolution_df.Time = weather_evolution_df.Time.astype('str').str[7:-3]
    weather_evolution_df.Humidity = weather_evolution_df.Humidity.astype('int')
    weather_evolution_df = weather_evolution_df.drop(columns=['Time_sec', 'WindDirection'])
    st.dataframe(weather_evolution_df, 
                     hide_index=True, height=185)

with col_row_2[1]:
    messages = fastf1.api.race_control_messages(session.api_path)
    messages_df = pd.DataFrame.from_dict(messages)
    if race_session == 'Race' or race_session == 'Sprint':
        messages_df['Message'] = messages_df.Flag.astype(str) + '/' + 'Lap ' + messages_df.Lap.astype(str) + ': ' + messages_df['Message']
        messages_df = messages_df[messages_df['Lap'] <=Lap_Number]
    elif race_session ==  'Qualifying' or race_session == 'Sprint Qualifying' or race_session == 'Practice 1' or race_session == 'Practice 2' or race_session == 'Practice 3':
        messages_df['Message'] = messages_df.Flag.astype(str) + '/' + messages_df['Message']

    messages_df= messages_df.drop(columns=['Category', 'Status', 'Scope', 'Sector', 'RacingNumber', 'Lap', 'Flag'])
    messages_df = messages_df.fillna('None')
    messages_df =messages_df.sort_values(['Time'], ascending=False)
    style_df = messages_df.style
    style_df = style_df.apply(flag_color_row, subset=['Message'], axis=1)
    style_df = style_df.apply(color_df, subset=['Time'], color='white')
    
    formatters = {
        'Message': lambda x: str(x).split('/')[1] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in messages_df.columns}
    style_df = style_df.format(final_formatters)
    st.dataframe(style_df, hide_index=True, height=185)


with col_row_2[2]:
    driver_data_all_laps = []
    if Lap_Number<10:
        lap_range =range(0, Lap_Number)
    else :
        lap_range = range(Lap_Number-10, Lap_Number)
    for lap in lap_range:
        LapTimePerLap = []
        driver_list = []
        for driver in session.drivers:
            try:
                driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number + 1))
                driver_data = str(driver_lap.LapTime.iloc[lap]).split(' ')[2]  + ' ' + str(driver_lap.Compound.iloc[lap]) + ' ' + str(driver_lap.PitInTime.iloc[lap]) + ' '  + str(driver_lap.PitOutTime.iloc[lap])
            except:
                driver_data = 'Ø No-data'
            if driver_data.split(' ')[0] == 'NaT':
                driver_data = 'Ø No-data'
            if driver_data != 'Ø No-data':
                if driver_data.split(' ')[2] != 'NaT':
                    driver_data = driver_data.split(' ')[1] + ' ' + 'PIT-IN'
                elif driver_data.split(' ')[3] != 'NaT':
                    driver_data = driver_data.split(' ')[1] + ' ' + 'OUT'
            driver_list.append(driver_lap.Driver.iloc[0] + ' ❚ '+ driver)
            LapTimePerLap.append(driver_data)
        LapTimePerLapSeries = pd.Series(LapTimePerLap, index=driver_list)
        driver_data_all_laps.append(LapTimePerLapSeries)
    driver_data_all_laps_df = pd.DataFrame(driver_data_all_laps)
    driver_data_all_laps_df = driver_data_all_laps_df.fillna('Ø No-data')
    if Lap_Number > 10 :
        driver_data_all_laps_df.index = range(Lap_Number-9, Lap_Number+1)
    else:
        driver_data_all_laps_df.index = range(1, Lap_Number+1)
    styled_df = driver_data_all_laps_df.style

    styled_df.set_properties(**{'color': 'black'})

    styled_df = styled_df.apply(background_color_df)

    header_styles = []
    for i, col in enumerate(driver_data_all_laps_df.columns):
        driver_short_name = col.split(' ')[0]
        try:
            driver_color = fastf1.plotting.get_driver_color(driver_short_name, session)
        except Exception: 
            driver_color = '#000000' 
        header_styles.append({
            'selector': f'th.col_heading.col{i}',
            'props': [('color', driver_color)]
        })

    styled_df = styled_df.set_table_styles(header_styles, overwrite=False)

    formatters = {}
    for driver in driver_list:
        formatters[driver] = lambda x: (
            str(x)[4:12]
            if len(str(x).split(' ')) >= 4
            else x.split(' ')[1]
        )

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_all_laps_df.columns}
    styled_df = styled_df.format(final_formatters)

    overall_fastest = np.min(driver_data_all_laps_df).split(' ')[0]
    for driver in driver_data_all_laps_df.columns:
        driver_lap = session.laps.pick_drivers(driver.split(' ')[0]).pick_laps(range(0, Lap_Number + 1))
        if str(np.min(driver_lap.LapTime)) != 'NaT':
            driver_fastest_lap = str(np.min(driver_lap.LapTime)).split(' ')[2]
        else:
            driver_fastest_lap = 0
        styled_df.apply(fastest_per_driver, subset= [f'{driver}'], driver_fastest_lap=driver_fastest_lap)

    header_styles = []
    for i, col in enumerate(driver_data_all_laps_df.columns):
        driver_short_name = col.split(' ')[0]
        try:
            driver_color = fastf1.plotting.get_driver_color(driver_short_name, session)
        except Exception: 
            driver_color = '#000000' 
        header_styles.append({
            'selector': f'th.col_heading.col{i}',
            'props': [('color', driver_color)]
        })
    styled_df = styled_df.set_table_styles(header_styles, overwrite=False)
    html_table = styled_df.to_html()
    #st.markdown(html_table, unsafe_allow_html=True, width="content")
    st.dataframe(styled_df)

with col_row_3[1]:
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector1', 'Gap', 'Tyre']
    for driver in session.drivers:
        driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number+1))
        try:
            index_fastest = driver_lap.Sector1Time[driver_lap.Sector1Time == np.min(driver_lap.Sector1Time)].index
            driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], np.min(driver_lap.Sector1Time), 0, driver_lap.Compound.loc[index_fastest[0]]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector1')
    driver_data_best_laps_df['Tyre'] = driver_data_best_laps_df.Tyre.replace(to_replace=tyres)
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df['Sector1'] - driver_data_best_laps_df['Sector1'].iloc[0])/driver_data_best_laps_df['Sector1'].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(color_df, subset=['Sector1'], color ='orange')
    styled_df = styled_df.apply(color_df, subset=['Gap'], color ='orange')

    formatters = {
        'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)
    
with col_row_3[2]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector2', 'Gap', 'Tyre']
    for driver in session.drivers:
        driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number+1))
        try:
            index_fastest = driver_lap.Sector2Time[driver_lap.Sector2Time == np.min(driver_lap.Sector2Time)].index
            driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], np.min(driver_lap.Sector2Time), 0, driver_lap.Compound.loc[index_fastest[0]]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector2')
    driver_data_best_laps_df['Tyre'] = driver_data_best_laps_df.Tyre.replace(to_replace=tyres)
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df['Sector2'] - driver_data_best_laps_df['Sector2'].iloc[0])/driver_data_best_laps_df['Sector2'].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(color_df, subset=['Sector2'], color ='orange')
    styled_df = styled_df.apply(color_df, subset=['Gap'], color ='orange')

    formatters = {
        'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)
    
with col_row_3[3]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector3', 'Gap', 'Tyre']
    for driver in session.drivers:
        driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number+1))
        try:
            index_fastest = driver_lap.Sector3Time[driver_lap.Sector3Time == np.min(driver_lap.Sector3Time)].index
            driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], np.min(driver_lap.Sector3Time), 0, driver_lap.Compound.loc[index_fastest[0]]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector3')
    driver_data_best_laps_df['Tyre'] = driver_data_best_laps_df.Tyre.replace(to_replace=tyres)
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df['Sector3'] - driver_data_best_laps_df['Sector3'].iloc[0])/driver_data_best_laps_df['Sector3'].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(color_df, subset=['Sector3'], color ='orange')
    styled_df = styled_df.apply(color_df, subset=['Gap'], color ='orange')

    formatters = {
        'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)

with col_row_3[4]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'LapTime', 'Gap', 'Tyre']
    for driver in session.drivers:
        driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number+1))
        try:
            index_fastest = driver_lap.LapTime[driver_lap.LapTime == np.min(driver_lap.LapTime)].index
            driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], np.min(driver_lap.LapTime), 0, driver_lap.Compound.loc[index_fastest[0]]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('LapTime')
    driver_data_best_laps_df['Tyre'] = driver_data_best_laps_df.Tyre.replace(to_replace=tyres)
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df['LapTime'] - driver_data_best_laps_df['LapTime'].iloc[0])/driver_data_best_laps_df['LapTime'].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(color_df, subset=['LapTime'], color ='orange')
    styled_df = styled_df.apply(color_df, subset=['Gap'], color ='orange')

    formatters = {
        'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)

with col_row_3[5]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'TheoraticalBest', 'Gap']
    for driver in session.drivers:
        driver_lap = session.laps.pick_drivers(driver).pick_laps(range(0, Lap_Number+1))
        try:
            driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], (np.min(driver_lap.Sector1Time) + np.min(driver_lap.Sector2Time) + np.min(driver_lap.Sector3Time)), 0]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('TheoraticalBest')
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df['TheoraticalBest'] - driver_data_best_laps_df['TheoraticalBest'].iloc[0])/driver_data_best_laps_df['TheoraticalBest'].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(color_df, subset=['TheoraticalBest'], color ='orange')
    styled_df = styled_df.apply(color_df, subset=['Gap'], color ='orange')

    formatters = {
        'TheoraticalBest': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)

with col_row_3[0]:
    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()
    circuit_info = session.get_circuit_info()

    track = pos.loc[:, ('X', 'Y')].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi

    rotated_track = rotate(track, angle=track_angle)

    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')

    ax.plot(rotated_track[:, 0], rotated_track[:, 1], linewidth=10, color='dimgrey')
    ax.tick_params(axis='x', which='both', bottom=False,
                    top=False, labelbottom=False)

    ax.tick_params(axis='y', which='both', right=False,
                    left=False, labelleft=False)
    each_lap = session.laps.pick_laps(range(0, Lap_Number))
    first_driver_session_time_in_microsec = int(str((each_lap.LapStartTime[each_lap.Position == 1 & (each_lap.LapNumber == max(each_lap.LapNumber))].values/1000)[0]).split(' ')[0])

    for driver in session.drivers:

        each_lap = session.laps.pick_laps(range(0, Lap_Number)).pick_drivers(driver)
        each_lap = each_lap[each_lap.Position == each_lap.Position]
        try:
            each_lap_data = each_lap.get_pos_data()
            
            each_lap_pos_data = each_lap_data.loc[:, ('X', 'Y')].to_numpy()
            each_lap_rotated_data = rotate(each_lap_pos_data, angle=track_angle)
            each_lap_data.loc[:, 'X'] = each_lap_rotated_data[:, 0]
            each_lap_data.loc[:, 'Y'] = each_lap_rotated_data[:, 1]
            
            txt = each_lap.Driver.iloc[0]

            pos_x = (each_lap_data['X'].iloc[(each_lap_data['SessionTime'] - timedelta(microseconds = first_driver_session_time_in_microsec)).abs().argsort()[:1]])
            pos_y = (each_lap_data['Y'].iloc[(each_lap_data['SessionTime'] - timedelta(microseconds = first_driver_session_time_in_microsec)).abs().argsort()[:1]])

            ax.scatter(pos_x.iloc[0], pos_y.iloc[0], color=fastf1.plotting.get_driver_color(txt, session=session), s=40, zorder=2)
            ax.text(pos_x.iloc[0], pos_y.iloc[0]+400, txt, color=fastf1.plotting.get_driver_color(txt, session=session), 
                    va='center_baseline', ha='center', size='x-large', zorder=3)
        except:
            continue
    st.pyplot(fig, clear_figure=True, transparent=True)