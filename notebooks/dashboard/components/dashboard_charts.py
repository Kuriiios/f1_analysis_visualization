import streamlit as st
import altair as alt
import data.fetch_data as dt
import numpy as np
import pandas as pd
import io
import base64
import fastf1
import fastf1.plotting
import fastf1.api
import matplotlib.pyplot as plt
from datetime import timedelta
import utils.format as fmt
import data.fetch_data as dt

def get_last_laps(session,  session_laps, race_session, Lap_Number, quali, height):
    
    driver_data_cols = [
        'Driver', 'Time',
        'Gap_ahead_Driver', 'Gap_to_Leader',
        'Sector1', 'I1', 'Sector2', 'I2', 'Sector3',
        'FL', 'LapTime', 'ST', 'Lap', 'Tyre', 'PitStop'
    ]
    fastest_lap_drivers = []
    for driver in session.drivers:
        if race_session == 'Race' or race_session == 'Sprint':
            fastest_lap_per_driver = session_laps.pick_drivers(driver).iloc[-1]
        else:
            fastest_lap_per_driver = session_laps.pick_drivers(driver).pick_fastest()
        try:
            if not fastest_lap_per_driver.empty:
                fastest_lap_per_driver = [
                    fastest_lap_per_driver.Driver  + ' ❚ ' + fastest_lap_per_driver.DriverNumber,
                    fastest_lap_per_driver.Time, 0, 0, fastest_lap_per_driver.Sector1Time, fastest_lap_per_driver.SpeedI1,
                    fastest_lap_per_driver.Sector2Time, fastest_lap_per_driver.SpeedI2, fastest_lap_per_driver.Sector3Time,
                    fastest_lap_per_driver.SpeedFL, fastest_lap_per_driver.LapTime, fastest_lap_per_driver.SpeedST,
                    fastest_lap_per_driver.LapNumber, fastest_lap_per_driver.Compound, (fastest_lap_per_driver.Stint - 1)
                ]

                fastest_lap_drivers.append(pd.Series(fastest_lap_per_driver, index=driver_data_cols)) 
        except:
            continue
    fastest_laps = pd.DataFrame(fastest_lap_drivers)
    if race_session == 'Race' or race_session == 'Sprint':
        fastest_laps = fastest_laps.sort_values(by=['Lap', 'Time'], ascending=[False, True])
        fastest_laps['Gap_ahead_Driver'] = fastest_laps['Time'].diff()
        fastest_laps['Gap_to_Leader'] = fastest_laps['Time'] - fastest_laps['Time'].iloc[0]
    else:
        fastest_laps = fastest_laps.sort_values(['LapTime'])
        fastest_laps['Gap_ahead_Driver'] = fastest_laps['LapTime'].diff()
        fastest_laps['Gap_to_Leader'] = fastest_laps['LapTime'] - fastest_laps['LapTime'].iloc[0]

    if fastest_laps.empty:
        print(f"No driver data collected for this scenario. Check session data and logic.")
    else:
        styled_df = fmt.style_lap_df(fastest_laps, session, Lap_Number)
    
    st.dataframe(styled_df, height=height)

def get_lap_and_tyre(session, session_laps, Lap_Number, height):
    driver_data_all_laps = []
    if Lap_Number<10:
        lap_range =range(0, Lap_Number+1)
    else :
        lap_range = range(Lap_Number-9, Lap_Number+1)
    for lap in lap_range:

        LapTimePerLap = []
        driver_list = []
        for driver in session.drivers:
            
            try:
                driver_lap = session_laps.pick_laps(lap).pick_drivers(driver)
                driver_data = str(driver_lap.LapTime.iloc[0]).split(' ')[2]  + ' ' + str(driver_lap.Compound.iloc[0]) + ' ' + str(driver_lap.PitInTime.iloc[0]) + ' '  + str(driver_lap.PitOutTime.iloc[0])
            except:
                continue
            if driver_data.split(' ')[0] == 'NaT':
                driver_data = 'Ø No-data'
            if driver_data != 'Ø No-data':
                if driver_data.split(' ')[2] != 'NaT':
                    driver_data = driver_data.split(' ')[1] + ' ' + 'PIT-IN'
                elif driver_data.split(' ')[3] != 'NaT':
                    driver_data = driver_data.split(' ')[1] + ' ' + 'OUT'
           
            driver_list.append(driver)
            LapTimePerLap.append(driver_data)   
            
        LapTimePerLapSeries = pd.Series(LapTimePerLap, index=driver_list)
        driver_data_all_laps.append(LapTimePerLapSeries)

    driver_data_all_laps_df = pd.DataFrame(driver_data_all_laps)
    driver_data_all_laps_df = driver_data_all_laps_df.fillna('Ø No-data')

    if Lap_Number<10 :
        driver_data_all_laps_df.index = range(1, Lap_Number+1)
    else:
        driver_data_all_laps_df.index = range(Lap_Number-9, Lap_Number+1)
    
    styled_df = driver_data_all_laps_df.style

    styled_df.set_properties(**{'color': 'black'})

    styled_df = styled_df.apply(fmt.background_color_df)
    
    formatters = {}
    for driver in session_laps.DriverNumber.unique():
        formatters[driver] = lambda x: (
            str(x)[4:12]
            if len(str(x).split(' ')) >= 4
            else x.split(' ')[1]
        )

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_all_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    
    overall_fastest = np.min(driver_data_all_laps_df).split(' ')[0]
    for driver in driver_data_all_laps_df.columns:
        driver_lap = session_laps.pick_drivers(driver.split(' ')[0]).pick_laps(range(0, Lap_Number + 1))
        if str(np.min(driver_lap.LapTime)) != 'NaT':
            driver_fastest_lap = str(np.min(driver_lap.LapTime)).split(' ')[2]
        else:
            driver_fastest_lap = 0
        styled_df.apply(fmt.fastest_per_driver, subset= [f'{driver}'], overall_fastest=overall_fastest, driver_fastest_lap=driver_fastest_lap)

    st.dataframe(styled_df, height=height)

def get_race_control_message(session, race_session, Lap_Number, height):
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
    style_df = style_df.apply(fmt.flag_color_row, subset=['Message'], axis=1)
    style_df = style_df.apply(fmt.color_df, subset=['Time'], color='white')
    
    formatters = {
        'Message': lambda x: str(x).split('/')[1] if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in messages_df.columns}
    style_df = style_df.format(final_formatters)
    st.dataframe(style_df, hide_index=True, height=int(height/2))

def get_weather_info(session, session_laps, Lap_Number, height):
    first_driver = session_laps.pick_drivers(session.drivers).pick_laps(Lap_Number)
    first_driver = first_driver[first_driver['Position'] == 1]
    weather_driver_lap = session_laps.get_weather_data()
    weather_driver_lap = weather_driver_lap.drop_duplicates()
    weather_driver_lap = weather_driver_lap.sort_values(['Time'])
    weather_driver_lap['Direction'] = weather_driver_lap['WindDirection'].apply(fmt.get_wind_direction_cat)
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
    st.dataframe(weather_evolution_df, hide_index=True, height=int(height/2))


def get_team_radio_chart(session, year, race_number, height):
    st.dataframe(dt.get_team_radio(session, year, race_number), height=height)

def get_last_laps_per_driver(session, session_laps, Lap_Number, driver, height):
    driver_data_last_laps = []
    driver_data_cols = ['Time', 'Lap', 'Sector1', 'I1', 'Sector2', 'I2', 'Sector3', 'FL', 'LapTime', 'ST']
    driver_lap = session_laps.pick_drivers(driver)
    if not driver_lap.empty:
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

        styled_df = styled_df.apply(fmt.highlight, subset=['Sector1'], min_max='min')
        styled_df = styled_df.apply(fmt.highlight, subset=['I1'], min_max='max')
        styled_df = styled_df.apply(fmt.highlight, subset=['Sector2'], min_max='min')
        styled_df = styled_df.apply(fmt.highlight, subset=['I2'], min_max='max')
        styled_df = styled_df.apply(fmt.highlight, subset=['Sector3'], min_max='min')
        styled_df = styled_df.apply(fmt.highlight, subset=['FL'], min_max='max')
        styled_df = styled_df.apply(fmt.highlight, subset=['LapTime'], min_max='min')
        styled_df = styled_df.apply(fmt.highlight, subset=['ST'], min_max='max')

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
        st.dataframe(styled_df, hide_index=True, height=height)

def get_track_status(session, session_laps, Lap_Number, height):
    on_track = []
    on_track_df = []
    on_track_logo = []
    each_lap = session_laps.pick_laps(range(0, Lap_Number))

    for driver in session.drivers:

        each_lap = session_laps.pick_laps(range(0, Lap_Number)).pick_drivers(driver)
        each_lap = each_lap[each_lap.Position == each_lap.Position]
        try:
            on_track.append('On Track')
            on_track_logo.append('🟢')
        except:
            on_track.append('DNF')
            on_track_logo.append('🔴')
    on_track_df = pd.DataFrame({
        'Status':on_track,
        'PU':on_track_logo}, index = session.drivers)
    st.dataframe(on_track_df, height=height) 

def get_map(session, session_laps, race_session, Lap_Number, minute, height):
    lap = session_laps.pick_fastest()
    pos = lap.get_pos_data()
    circuit_info = session.get_circuit_info()

    track = pos.loc[:, ('X', 'Y')].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi

    rotated_track = fmt.rotate(track, angle=track_angle)

    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect('equal', adjustable='box')

    ax.plot(rotated_track[:, 0], rotated_track[:, 1], linewidth=10, color='dimgrey')
    ax.tick_params(axis='x', which='both', bottom=False,
                    top=False, labelbottom=False)

    ax.tick_params(axis='y', which='both', right=False,
                    left=False, labelleft=False)
    
    if race_session == 'Race' or race_session == 'Sprint' :
        each_lap = session_laps.pick_laps(range(0, Lap_Number))
        first_driver_session_time_in_microsec = int(str((each_lap.LapStartTime[each_lap.Position == 1 & (each_lap.LapNumber == max(each_lap.LapNumber))].values/1000)[0]).split(' ')[0])
    else:
        each_lap = session_laps

    for driver in session.drivers:
        if race_session == 'Race' or race_session == 'Sprint':
            each_lap = session_laps.pick_laps(range(0, Lap_Number+1)).pick_drivers(driver)
        else:
            each_lap = session_laps.pick_drivers(driver)
        try:
            each_lap_data = each_lap.get_pos_data()
            each_lap_pos_data = each_lap_data.loc[:, ('X', 'Y')].to_numpy()
            each_lap_rotated_data = fmt.rotate(each_lap_pos_data, angle=track_angle)
            each_lap_data.loc[:, 'X'] = each_lap_rotated_data[:, 0]
            each_lap_data.loc[:, 'Y'] = each_lap_rotated_data[:, 1]
            
            txt = each_lap.Driver.iloc[0]
        
            if race_session == 'Race' or race_session == 'Sprint':
                pos_x = (each_lap_data['X'].iloc[(each_lap_data['SessionTime'] - timedelta(microseconds = first_driver_session_time_in_microsec)).abs().argsort()[:1]])
                pos_y = (each_lap_data['Y'].iloc[(each_lap_data['SessionTime'] - timedelta(microseconds = first_driver_session_time_in_microsec)).abs().argsort()[:1]])
            else:
                pos_x = each_lap_data['X'][each_lap_data['SessionTime'] > timedelta(seconds=each_lap.Time.iloc[0].total_seconds() + (minute * 60))].iloc[0]
                pos_y = each_lap_data['Y'][each_lap_data['SessionTime'] > timedelta(seconds=each_lap.Time.iloc[0].total_seconds() + (minute * 60))].iloc[0]
            ax.scatter(pos_x, pos_y, color=fastf1.plotting.get_driver_color(txt, session=session), s=40, zorder=2)
            ax.text(pos_x, pos_y+400, txt, color=fastf1.plotting.get_driver_color(txt, session=session), 
                    va='center_baseline', ha='center', size='x-large', zorder=3)
        except:
            continue
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', transparent=True)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")

    html = f"""
    <div style="
    height: {height};
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    ">
        <img src="data:image/png;base64,{image_base64}" style="max-height: {height}; object-fit: cover;" />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def get_best(session, session_laps, Lap_Number, column_name, column, unit, height):
    match unit:
        case 's':
            substract = 13
        case 'm':
            substract = 11
    driver_data_best_laps = []
    if column != 'TheoraticalBest':
        driver_data_cols = ['Driver', column_name, 'Gap', 'Tyre']
    else:
        driver_data_cols = ['Driver', column_name, 'Gap']
    for driver in session.drivers:
        driver_lap = session_laps.pick_drivers(driver).pick_laps(range(0, Lap_Number + 1))
        try:
            if column == 'TheoraticalBest':
                driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], (np.min(driver_lap.Sector1Time) + np.min(driver_lap.Sector2Time) + np.min(driver_lap.Sector3Time)), 0]
            else :
                index_fastest = driver_lap[column][driver_lap[column] == np.min(driver_lap[column])].index
                driver_data = [driver_lap.Driver.iloc[0] + ' ❚ ' + driver_lap.DriverNumber.iloc[0], np.min(driver_lap[column]), 0, driver_lap.Compound.loc[index_fastest[0]]]
        except:
            continue
        driver_data_series = pd.Series(driver_data, index=driver_data_cols)
        driver_data_best_laps.append(driver_data_series)
    driver_data_best_laps_df = pd.DataFrame(driver_data_best_laps)
    driver_data_best_laps_df = driver_data_best_laps_df.sort_values(column_name)
    if column != 'TheoraticalBest':
        driver_data_best_laps_df['Tyre'] = driver_data_best_laps_df.Tyre.replace(to_replace=dt.tyres)
    driver_data_best_laps_df['Gap'] = ((driver_data_best_laps_df[column_name] - driver_data_best_laps_df[column_name].iloc[0])/driver_data_best_laps_df[column_name].iloc[0])*100
    styled_df = driver_data_best_laps_df.style
    styled_df = styled_df.apply(fmt.highlight_driver, subset=['Driver'], session= session)
    styled_df = styled_df.apply(fmt.color_df, subset=[column_name], color ='orange')
    styled_df = styled_df.apply(fmt.color_df, subset=['Gap'], color ='orange')

    formatters = {
        column_name: lambda x: str(x)[substract:-3] if pd.notnull(x) else 'No Data',
        'Gap': lambda x: str(round(x,1))+'%' if pd.notnull(x) else 'No Data',
    }

    final_formatters = {k: v for k, v in formatters.items() if k in driver_data_best_laps_df.columns}
    styled_df = styled_df.format(final_formatters)
    st.dataframe(styled_df, hide_index=True, height=height)