import numpy as np
import fastf1
import fastf1.plotting
import pandas as pd
import os

def show_driver_delta(team, team_drivers, quali_session, circuit_info, delta_per_team, sub_session):
    """
    Calculates and stores the delta time between two drivers of a team.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        circuit_info (fastf1.core.Circuit): Circuit information.
        delta_per_team (dict): Dictionary to store delta times for each team.
        sub_session (str): The current sub-session (e.g., 'Q1', 'Q2', 'Q3').

    Returns:
        dict: Updated delta_per_team dictionary.  Stores delta times at corners.
    """
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()

    if driver_1_lap is not None and driver_2_lap is not None:
        delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(driver_1_lap, driver_2_lap)
        delta_time_at_corner = [0]
        for idx_corner, corner in circuit_info.corners.iterrows():
            for idx_dist, dist in ref_tel['Distance'].items():
                if dist > corner['Distance']:
                    delta_time_at_corner.append(round(delta_time[idx_dist], 3))
                    break
        delta_time_at_corner.append(round(delta_time.iloc[-1], 3))
        delta_time_at_corner_diff = np.diff(delta_time_at_corner).tolist()
        delta_time_at_corner_diff = [round(elem, 3) for elem in delta_time_at_corner_diff]
        delta_per_team.update({f'{sub_session}_{team}': delta_time_at_corner_diff})
        return delta_per_team

def show_corner_segments(team, team_drivers, quali_session, circuit_info, corner_segments, sub_session):
    """
    Calculates and stores corner segment lengths.

    Args:
        team_drivers (list): List of driver abbreviations.
        quali_session (fastf1.core.Session): Session data.
        circuit_info (fastf1.core.Circuit): Circuit information.
        corner_segments (dict): Dictionary to store corner segment lengths.
        sub_session (str): Current sub-session.

    Returns:
        dict: Updated corner_segments dictionary.
    """
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    corner_segments_list = [0]
    if driver_1_lap is not None and driver_2_lap is not None:
        delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(driver_1_lap, driver_2_lap) # Added to avoid potential error.  Not used.
        figure_diff = max(ref_tel['Distance']) / 994
        for idx_corner, corner in circuit_info.corners.iterrows():
            corner_segments_list.append(corner['Distance'] / figure_diff)
        figure_width = 994
        corner_segments_list.append(figure_width)
        corner_segments_diff = np.diff(corner_segments_list).tolist()
        corner_segments_diff = [elem for elem in corner_segments_diff]
        corner_segments.update({f'{sub_session}_{team}': corner_segments_diff})
        return corner_segments

def create_csv_lap_info(quali_session, list, team, sub_session, event_name, race_session, delta_per_team, circuit_info, session):
    """
    Extracts and formats lap information for saving to a CSV file.

    Args:
        quali_session (fastf1.core.Session): The qualifying session data.
        list (list): The list to append the driver information to.
        team (str): The team name.
        sub_session (str): The current sub-session.
        event_name (str): Name of the event.
        race_session (str): Type of race session ('Q' or 'SQ').
        delta_per_team (dict): Dictionary containing delta times.
        circuit_info (fastf1.core.Circuit): Circuit information.
        session (fastf1.core.Session): complete session.

    Returns:
        list: Updated list containing the formatted lap information.
    """
    driver_info_csv = list
    if race_session == 'Q':
        event_title = event_name.split(' ', 1)[0] + ' GP Qualifying ' + sub_session
    elif race_session == 'SQ':
        event_title = event_name.split(' ', 1)[0] + ' GP Sprint Quali ' + sub_session

    v_min = 1000
    v_max = 0
    delta_by_team = delta_per_team.get(f'{sub_session}_{team}', [])  # Use .get() to avoid KeyError
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    corner_advantage_driver_1 = str(len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >= 0])) + '/' + str(len(delta_by_team)) if delta_by_team else "0/0"
    corner_advantage_driver_2 = str(len(delta_by_team) - len([float(delta_at_corner) for delta_at_corner in delta_by_team if float(delta_at_corner) >= 0])) + '/' + str(len(delta_by_team)) if delta_by_team else "0/0"
    corner_advantage_team = [corner_advantage_driver_1, corner_advantage_driver_2]
    
    team_info = [
        event_title,
    ]
    
    if team_drivers[0] in  quali_session['Driver'].values and team_drivers[1] in  quali_session['Driver'].values:
        for driver in team_drivers:
            driver_lap = quali_session.pick_drivers(driver).pick_fastest()
            if driver_lap is not None:
                driver_name = fastf1.plotting.get_driver_name(driver, session)
                if driver_name == 'Andrea Kimi Antonelli':
                    driver_name = 'Kimi Antonelli'
                elif driver_name == 'Oliver Bearman':
                    driver_name = 'Ollie Bearman'
                driver_tel = driver_lap.get_car_data()
                full_throttle = round(len(np.where(driver_tel['Throttle'].values >= 90)[0]) / len(driver_tel) * 100)
                brake = round(len(np.where(driver_tel['Brake'] == True)[0]) / len(driver_tel) * 100)
                cornering = 100 - full_throttle - brake
                v_min = int(min(v_min, min(driver_tel['Speed'])))
                v_max = int(max(v_max, max(driver_tel['Speed'])))

                try:
                    SpeedI1 = str(int(driver_lap['SpeedI1'])) + ' kp/h'
                except ValueError:
                    SpeedI1 = 'No data'

                if len(str(driver_lap['LapTime'])) == 15:
                    laptime = str(driver_lap['LapTime'])[10:] + '.000'
                else:
                    laptime = str(driver_lap['LapTime'])[10:-3]

                driver_info = [
                    driver_name,
                    laptime,
                    str(driver_lap['Sector1Time'])[13:-3],
                    str(driver_lap['Sector2Time'])[13:-3],
                    str(driver_lap['Sector3Time'])[13:-3],
                    SpeedI1,
                    str(int(driver_lap['SpeedI2'])) + ' kp/h',
                    str(int(driver_lap['SpeedFL'])) + ' kp/h',
                    str(full_throttle) + '%',
                    str(brake) + '%',
                    str(cornering) + '%',
                ]
                team_info.extend(driver_info)
            else:
                #  Add "No data" if driver_lap is None
                team_info.extend(['No data'] * 11)
        try:
            gap = round(float(team_info[2][3:]) - float(team_info[13][3:]), 3)
            gap1 = round(float(team_info[13][3:]) - float(team_info[2][3:]), 3)
        except ValueError:
            gap = 'No data'
            gap1 = 'No data'
        gaps = [gap, gap1]
        team_info.extend(gaps)
            
        v_speed = [str(v_min) + ' kp/h', str(v_max) + ' kp/h']
        team_info.extend(v_speed)
        team_info.extend(corner_advantage_team)
        driver_info_csv.append(team_info)
    return driver_info_csv