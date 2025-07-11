import fastf1
import fastf1.api
import fastf1.plotting
from fastf1.ergast import Ergast

import pandas as pd
import numpy as np
from datetime import timedelta
import seaborn as sns

import streamlit as st
import altair as alt 
import plotly.express

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
    race_number = st.selectbox('Select a race', race_list)

    #session_list = ['Practice 1', 'Practice 2', 'Practice 3', 'Sprint Qualifying', 'Sprint Race', 'Qualifying', 'Race']
    session_list = ['Race']
    race_session = st.selectbox('Select a session', session_list, index=len(session_list)-1)

    lap_list = list(range(1, 79))
    Lap_Number = st.selectbox('Select a lap', lap_list)

    team_list = ['Red Bull Racing', 'Alpine', 'Mercedes', 'Aston Martin', 'Ferrari', 'Williams', 'Kick Sauber', 'Racing Bulls', 'Haas F1 Team', 'McLaren']
    team = st.selectbox('Select a lap', team_list, index=4)

def highlight(s, min_max):
    if min_max == 'min':
        is_min_max = s == s.min()
    if min_max == 'max':
        is_min_max = s == s.min()

    return ['color: green' if v else 'color: orange' for v in is_min_max]

def highlight_compound(s):
    colors = []
    for compound_value in s:
        if compound_value == 'SOFT':
            colors.append('color: red')
        elif compound_value == 'MEDIUM':
            colors.append('color: yellow')
        elif compound_value == 'HARD':
            colors.append('color: white')
        elif compound_value == 'INTERMEDIATE':
            colors.append('color: green')
        elif compound_value == 'WET':
            colors.append('color: blue')
        else:
            colors.append('color: grey')
    return colors

def highlight_driver(s):
    drivers = []
    for driver_name in s:
        if driver_name == 'VER' or driver_name == 'TSU':
            drivers.append('color: #0600ef')
        elif driver_name == 'GAS' or driver_name == 'DOO' or driver_name == 'COL':
            drivers.append('color: #ff87bc')
        elif driver_name == 'RUS' or driver_name == 'ANT':
            drivers.append('color: #27f4d2')
        elif driver_name == 'ALO' or driver_name == 'STR':
            drivers.append('color: #00665f')
        elif driver_name == 'LEC' or driver_name == 'HAM':
            drivers.append('color: #e80020')
        elif driver_name == 'ALB' or driver_name == 'SAI':
            drivers.append('color: #00a0dd')
        elif driver_name == 'HUL' or driver_name == 'BOR':
            drivers.append('color: #00e700')
        elif driver_name == 'HAD' or driver_name == 'LAW':
            drivers.append('color: #fcd700')
        elif driver_name == 'BEA' or driver_name == 'OCO':
            drivers.append('color: #b6babd')
        elif driver_name == 'NOR' or driver_name == 'PIA':
            drivers.append('color: #ff8000')
        else:
            drivers.append('color: grey')
    return drivers

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

session= fastf1.get_session(year, race_number, race_session)
session.load()

#pit = ergast.get_pit_stops(season = year, round = race_number )
teams = fastf1.plotting.list_team_names(session)
team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
event_name = session.event.EventName

col_row_1 = st.columns((1.5, 1, 1), gap='small')
col_row_2 = st.columns((1, 1, 2), gap='small')
col_row_3 = st.columns((1, 1, 1, 1, 1), gap='small')

with col_row_1[1]:
    driver_data_last_laps = []
    for lap in range(Lap_Number-9,Lap_Number+1):
        driver_data_cols = ['Time', 'Lap', 'Sector1', 'I1', 'Sector2', 'I2', 'Sector3', 'FL', 'LapTime', 'ST']
        driver = team_drivers[0]
        driver_lap = session.laps.pick_drivers(driver)
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

with col_row_1[2]:
    driver_data_last_laps = []
    for lap in range(Lap_Number-9,Lap_Number+1):
        driver_data_cols = ['Time', 'Lap', 'Sector1', 'I1', 'Sector2', 'I2', 'Sector3', 'FL', 'LapTime', 'ST']
        driver = team_drivers[1]
        driver_lap = session.laps.pick_drivers(driver)
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
    drivers_data = []
    driver_data_cols = [
        'Position', '№_Driver', 'Driver_Color', 'Driver', 'Time',
        'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
        'FL', 'LapTime', 'ST', 'Lap', 'Compound', 'PitStop'
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
            leader_color = fastf1.plotting.get_driver_color(leader_snapshot_lap_data.Driver, session)
            leader_data = [
                leader_snapshot_lap_data.Position, leader_driver_number, leader_color, leader_snapshot_lap_data.Driver,
                leader_snapshot_lap_data.Time, leader_snapshot_lap_data.Sector1Time, leader_snapshot_lap_data.SpeedI1,
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
                driver_color = fastf1.plotting.get_driver_color(selected_lap.Driver, session)
                driver_data = [
                    selected_lap.Position, driver_num, driver_color, selected_lap.Driver,
                    selected_lap.Time, selected_lap.Sector1Time, selected_lap.SpeedI1,
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

        drivers_data_df['Time_td'] = drivers_data_df['Time']
        drivers_data_df['Gap_ahead_Driver'] = drivers_data_df['Time_td'].diff()
        drivers_data_df['Gap_to_Leader'] = drivers_data_df['Time_td'] - drivers_data_df['Time_td'].iloc[0]
        for col in ['Sector1', 'Sector2', 'Sector3', 'LapTime']:
            if pd.api.types.is_timedelta64_dtype(drivers_data_df[col]):
                drivers_data_df[col] = drivers_data_df[col].astype(str).str[13:-3]
            elif isinstance(drivers_data_df[col].iloc[0], pd.Timedelta):
                drivers_data_df[col] = drivers_data_df[col].astype(str).str[13:-3]
            else:
                drivers_data_df[col] = drivers_data_df[col].astype(str)

        drivers_data_df = drivers_data_df.drop(columns=['Time_td', 'Driver_Color'])
        drivers_data_df = drivers_data_df[drivers_data_df['Position']>0]

        styled_df = drivers_data_df.style
        styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
        styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

        formatters = {
        
        'Position': lambda x: int(x) if pd.notnull(x) else 'No Data',
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
        'Gap_ahead_Driver': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
        'Gap_to_Leader': lambda x: str(x)[7:-3] if pd.notnull(x) else 'No Data',
        }

        final_formatters = {k: v for k, v in formatters.items() if k in drivers_data_df.columns}
        styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                        hide_index=True)

with col_row_2[0]:
    weather_driver_lap = session.laps.get_weather_data()
    weather_driver_lap['Direction'] = weather_driver_lap['WindDirection'].apply(get_wind_direction_cat)
    i = np.argmin(np.abs(weather_driver_lap.Time - timedelta(hours=1)))
    i_10min = np.argmin(np.abs(weather_driver_lap.Time - timedelta(hours=1, minutes=10)))
    i_10plus = np.argmin(np.abs(weather_driver_lap.Time - timedelta(minutes=50)))
    weather_evolution = [weather_driver_lap.iloc[i_10min], weather_driver_lap.iloc[i], weather_driver_lap.iloc[i_10plus]]
    weather_evolution_df = pd.DataFrame(weather_evolution)
    weather_evolution_df.Time = weather_evolution_df.Time.astype('str').str[7:-3]
    weather_evolution_df.Humidity = weather_evolution_df.Humidity.astype('int')
    st.dataframe(weather_evolution_df, 
                     hide_index=True)

with col_row_2[1]:
    messages = fastf1.api.race_control_messages(session.api_path)
    messages_df = pd.DataFrame.from_dict(messages)
    messages_df= messages_df.drop(columns=['Category', 'Status', 'Scope', 'Sector', 'RacingNumber'])
    st.dataframe(messages_df, 
                     hide_index=True)

with col_row_2[2]:
    driver_data_all_laps = []
    lap_range = range(lap-10,lap+1)
    for lap in lap_range:
        LapTimePerLap = []
        for driver in session.drivers:
            try:
                driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1,53))
                driver_data = driver_lap.LapTime.iloc[lap]
            except:
                driver_data = timedelta(0)
            LapTimePerLap.append(driver_data)
        LapTimePerLapSeries = pd.Series(LapTimePerLap, index=session.drivers)
        driver_data_all_laps.append(LapTimePerLapSeries)
    driver_data_all_laps_df = pd.DataFrame(driver_data_all_laps)
    driver_data_all_laps_df = driver_data_all_laps_df.fillna(0)
    driver_data_all_laps_df = driver_data_all_laps_df.astype(str).apply(lambda x: x.str[11:-3])
    driver_data_all_laps_df['index'] = list(lap_range)
    driver_data_all_laps_df = driver_data_all_laps_df.set_index('index')
    st.dataframe(driver_data_all_laps_df, 
                     hide_index=True)

with col_row_3[0]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector1', 'Compound']
    for driver in session.drivers:
        try:
            driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1, 53))
            driver_data = [driver_lap.Driver.iloc[Lap_Number], np.min(driver_lap.Sector1Time), driver_lap.Compound.iloc[Lap_Number]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector1')
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

    formatters = {
        'Sector1': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)
    
with col_row_3[1]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector2', 'Compound']
    for driver in session.drivers:
        try:
            driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1, 53))
            driver_data = [driver_lap.Driver.iloc[Lap_Number], np.min(driver_lap.Sector2Time), driver_lap.Compound.iloc[Lap_Number]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector2')
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

    formatters = {
        'Sector2': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)
    
with col_row_3[2]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'Sector3', 'Compound']
    for driver in session.drivers:
        try:
            driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1, 53))
            driver_data = [driver_lap.Driver.iloc[Lap_Number], np.min(driver_lap.Sector3Time), driver_lap.Compound.iloc[Lap_Number]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('Sector3')
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

    formatters = {
        'Sector3': lambda x: str(x)[13:-3] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)

with col_row_3[3]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'LapTime', 'Compound']
    for driver in session.drivers:
        try:
            driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1, 53))
            driver_data = [driver_lap.Driver.iloc[Lap_Number], np.min(driver_lap.LapTime), driver_lap.Compound.iloc[Lap_Number]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('LapTime')
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

    formatters = {
        'LapTime': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)

with col_row_3[4]:
    driver_data_last_laps_df=pd.DataFrame()
    driver_data_best_laps = []
    driver_data_cols = ['Driver', 'TheoraticalBest', 'Compound']
    for driver in session.drivers:
        try:
            driver_lap = session.laps.pick_drivers(driver).pick_laps(range(1, 53))
            driver_data = [driver_lap.Driver.iloc[Lap_Number], (np.min(driver_lap.Sector1Time) + np.min(driver_lap.Sector2Time) + np.min(driver_lap.Sector3Time)), driver_lap.Compound.iloc[Lap_Number]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values('TheoraticalBest')
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(highlight_driver, subset=['Driver'])
    styled_df = styled_df.apply(highlight_compound, subset=['Compound'])

    formatters = {
        'TheoraticalBest': lambda x: str(x)[11:-3] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, 
                     hide_index=True)