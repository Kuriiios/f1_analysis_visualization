import fastf1
import fastf1.plotting
import numpy as np
import pandas as pd
import data.fetch_data as dt

def style_lap_df(df, session, Lap_Number):
    df['Tyre'] = df.Tyre.replace(to_replace = dt.tyres)
    df = df.sort_values(['LapTime'] if 'LapTime' in df else ['Position'])
    df['Gap_ahead_Driver'] = df['LapTime' if 'LapTime' in df else 'Time'].diff()
    df['Gap_to_Leader'] = df['LapTime' if 'LapTime' in df else 'Time'] - df.iloc[0]['LapTime' if 'LapTime' in df else 'Time']
    df.index = range(1, len(df) + 1)
    
    style_df = df.style
    style_df = style_df.apply(highlight_driver, subset=['Driver'], session = session)
    style_df = style_df.apply(is_personal_best, subset=['Sector1'], column='Sector1Time', extreme='min', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['Sector2'], column='Sector2Time', extreme='min', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['Sector3'], column='Sector3Time', extreme='min', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['LapTime'], column='LapTime', extreme='min', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['I1'], column='SpeedI1', extreme='max', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['I2'], column='SpeedI2', extreme='max', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['FL'], column='SpeedFL', extreme='max', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(is_personal_best, subset=['ST'], column='SpeedST', extreme='max', session = session, Lap_Number = Lap_Number)
    style_df = style_df.apply(color_df, subset=['Gap_ahead_Driver'], color='orange')
    style_df = style_df.apply(color_df, subset=['Gap_to_Leader'], color='orange')

    return style_df.format({
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
    })


def fastest_per_driver(subset, overall_fastest, driver_fastest_lap):
    colors = []
    for time in subset:
        if time.split(' ')[0] == overall_fastest:
            colors.append('color:purple')
        elif time.split(' ')[0] == driver_fastest_lap:
            colors.append('color:darkgreen')
        else:
            colors.append('color:black')
    return colors

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

def is_personal_best(subset, column, extreme ,session, Lap_Number):
    best_colors = []
    extreme_values = {}
    driver_ids = list(session.drivers)

    for driver_id in driver_ids:
        if extreme == 'min':
            extreme_values[driver_id] = session.laps.pick_drivers(driver_id).pick_laps(range(0, Lap_Number + 1))[column].min()
        elif extreme == 'max':
            extreme_values[driver_id] = session.laps.pick_drivers(driver_id).pick_laps(range(0, Lap_Number + 1))[column].max()

    all_driver_laps = session.laps.pick_drivers(session.drivers).pick_laps(range(0, Lap_Number + 1))
    if not all_driver_laps.empty:
        if extreme == 'min':
            overall_extreme = all_driver_laps[column].min()
        elif extreme == 'max':
            overall_extreme = all_driver_laps[column].max()
    else:
        if extreme == 'min':
            overall_extreme = 'inf'
        elif extreme == 'max':
            overall_extreme = 0

    for column_value in subset:
        color = 'color:orange'
        for driver in session.drivers:
            if column_value  == overall_extreme:
                color = 'color:purple'
            if column_value == extreme_values.get(driver):
                color = 'color:green'

        best_colors.append(color)

    return best_colors

def highlight(subset, min_max):
    if min_max == 'min':
        is_min_max = subset == subset.min()
    if min_max == 'max':
        is_min_max = subset == subset.max()
    return ['color: green' if v else 'color: orange' for v in is_min_max]


def highlight_driver(subset, session):
    drivers = []
    for driver_name in subset:
        driver_color = fastf1.plotting.get_driver_color(driver_name[0:3], session)
        drivers.append(f'color: {driver_color}')
    return drivers

def color_df(s, color):
    colors= []
    for driver_name in s:
        colors.append(f'color:{color}')
    return colors

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)