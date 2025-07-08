import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from matplotlib import colormaps
from chromato.spaces import convert
import fastf1
import fastf1.plotting

def rotate(xy, *, angle):
    """
    Rotates a 2D point or array of points by a given angle.

    Args:
        xy (numpy.ndarray): A 2D point or array of 2D points with shape (2,) or (N, 2).
        angle (float): The rotation angle in radians.

    Returns:
        numpy.ndarray: The rotated point or array of points.
    """
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def get_corner_dist_for_drivers(driver_tel, circuit_info):
    """
    Determines the distance along the track where each corner occurs for a driver.

    Args:
        driver_tel (pandas.DataFrame): Telemetry data for a driver, containing 'Distance' column.
        circuit_info (fastf1.core.Circuit): Information about the circuit, containing corner distances.

    Returns:
        list: A list of rows from driver_tel corresponding to corner distances.
    """
    driver_corner_distance = []
    i = 0
    for index, row in driver_tel.iterrows():
        distance = row['Distance']
        if i == len(circuit_info.corners):
            break
        elif distance > circuit_info.corners['Distance'][i]:
            driver_corner_distance.append(row)
            i += 1
    return driver_corner_distance

def add_turn(driver_tel, circuit_info):
    """
    Adds a 'Turn' column to the driver's telemetry data, indicating the turn number.

    Args:
        driver_tel (pandas.DataFrame): Telemetry data for a driver, containing 'Distance' column.
        circuit_info (fastf1.core.Circuit): Information about the circuit, containing corner distances.

    Returns:
        numpy.ndarray: An array of turn numbers corresponding to each distance in driver_tel.
    """
    driver_distance = get_corner_dist_for_drivers(driver_tel, circuit_info)

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

def add_faster_driver(driver_tel, faster_driver, circuit_info):
    """
    Adds a 'faster_driver' column to the driver's telemetry, indicating if the driver was faster in a given corner.

    Args:
        driver_tel (pandas.DataFrame): Telemetry data for a driver, containing 'Turn' column.
        faster_driver (list): A list indicating which driver was faster at each corner (1 for driver 1, 0 for driver 2).
        circuit_info (fastf1.core.Circuit): Circuit information.

    Returns:
        numpy.ndarray: An array indicating the faster driver for each point in the telemetry.
    """
    values = driver_tel['Turn'].values
    faster = np.zeros_like(values, dtype=int)
    for i, val in enumerate(faster_driver):
        if val == 1:
            faster[values == i + 1] = 1
    return faster

def convert_for_cmap(base_color):
    """
    Converts a hex color code to RGB format, scaled for matplotlib.

    Args:
        base_color (str): A hex color code (e.g., '#RRGGBB').

    Returns:
        tuple: A tuple of (r, g, b) values, scaled between 0 and 1.
    """
    base_color_rgb = convert.hex_to_rgb(base_color)
    r = base_color_rgb.r / 255
    g = base_color_rgb.g / 255
    b = base_color_rgb.b / 255
    return r, g, b

def get_delta_per_team(team, team_drivers, quali_session, circuit_info, subsession_name, delta_per_team):
    """
    Calculates the delta time between two drivers of a team and extracts delta time at each corner.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        circuit_info (fastf1.core.Circuit): Circuit information.
        subsession_name (str): Name of the subsession (e.g., 'Q1', 'Q2', 'Q3').
        delta_per_team (dict): Dictionary to store delta times for each team.

    Returns:
        dict: Updated delta_per_team dictionary.
    """
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()

    if driver_1_lap is not None and driver_2_lap is not None:
        delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(driver_1_lap, driver_2_lap)
        max_delta = max(abs(min(delta_time)), abs(max(delta_time))) + 0.1

        delta_time_at_corner = [0]
        for idx_corner, corner in circuit_info.corners.iterrows():
            for idx_dist, dist in ref_tel['Distance'].items():
                if dist > corner['Distance']:
                    delta_time_at_corner.append(round(delta_time[idx_dist], 3))
                    break
        delta_time_at_corner_diff = np.diff(delta_time_at_corner).tolist()
        delta_time_at_corner_diff = [round(elem, 3) for elem in delta_time_at_corner_diff]
        delta_per_team[f'{subsession_name}_{team}'] = delta_time_at_corner_diff
    return delta_per_team

def show_corner_advantage_per_quali_session(team, team_drivers, quali_session, circuit_info, subsession_name, team_color, team_color_2, delta_per_team, figures_folder):
    """
    Visualizes corner advantage by plotting the track and coloring segments based on which driver is faster.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        circuit_info (fastf1.core.Circuit): Information about the circuit.
        subsession_name (str): Name of the subsession (e.g., 'Q1', 'Q2', 'Q3').
        team_color (str): Hex color code for the first team driver.
        team_color_2 (str): Hex color code for the second team driver.
    """
    gaps = [1 if gap >= 0 else 0 for gap in delta_per_team[f'{subsession_name}_{team}']]

    lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    if lap is None:
        print(f"No fastest lap found for {team_drivers[0]} in {subsession_name}")
        return  # Exit if no fastest lap

    tel = lap.get_telemetry()
    tel['Turn'] = add_turn(tel, circuit_info)
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

    tc_r, tc_g, tc_b = convert_for_cmap(team_color)
    tc_r2, tc_g2, tc_b2 = convert_for_cmap(team_color_2)

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
    lc_comp = LineCollection(segments, linewidths=4, cmap=cmap)
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
    txt_sl = 'Start / Finish Line'
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
    plt.savefig(fname=figures_folder/f'{subsession_name}_{team}_corner_domination', transparent=True)
    plt.close(fig)  # Close the figure to prevent display


def create_bar_graph_per_driver(team, team_drivers, quali_session, subsession_name, team_color, team_color_2, figures_folder):
    """
    Creates bar graphs comparing throttle, braking, and cornering for each driver.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        subsession_name (str): Name of the subsession (e.g., 'Q1', 'Q2', 'Q3').
        team_color (str): Hex color code for the first team driver.
        team_color_2 (str): Hex color code for the second team driver.
    """
    driver_1_lap = quali_session.pick_drivers(team_drivers[0]).pick_fastest()
    driver_2_lap = quali_session.pick_drivers(team_drivers[1]).pick_fastest()
    if driver_1_lap is not None and driver_2_lap is not None:

        driver_1_tel = driver_1_lap.get_car_data()

        full_throttle = round(len(np.where(driver_1_tel['Throttle'].values >= 90)[0]) / len(driver_1_tel) * 100)
        brake = round(len(np.where(driver_1_tel['Brake'] == True)[0]) / len(driver_1_tel) * 100)
        cornering = 100 - full_throttle - brake

        driver_2_tel = driver_2_lap.get_car_data()

        full_throttle1 = round(len(np.where(driver_2_tel['Throttle'].values >= 90)[0]) / len(driver_2_tel) * 100)
        brake1 = round(len(np.where(driver_2_tel['Brake'] == True)[0]) / len(driver_2_tel) * 100)
        cornering1 = 100 - full_throttle - brake

        keys = ('Full Throttle', 'Braking', 'Cornering')

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
        plt.barh(keys[2], cornering_bar, height=0.4, color=['#696969', team_color])
        plt.barh(keys[1], brake_bar, height=0.4, color=['#696969', team_color])
        plt.barh(keys[0], full_throttle_bar, height=0.4, color=['#696969', team_color])
        plt.rcParams['axes.spines.left'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.bottom'] = False
        plt.savefig(fname= figures_folder /f'{subsession_name}_{team}_driver_1_bar_graph', transparent=True)
        plt.close()

        full_throttle_bar1 = np.array([100, full_throttle1])
        brake_bar1 = np.array([100, brake1])
        cornering_bar1 = np.array([100, cornering1])
        plt.subplots(figsize=(5, 2))
        plt.barh(keys[2], cornering_bar1, height=0.4, color=['#696969', team_color_2])
        plt.barh(keys[1], brake_bar1, height=0.4, color=['#696969', team_color_2])
        plt.barh(keys[0], full_throttle_bar1, height=0.4, color=['#696969', team_color_2])
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
        plt.savefig(fname= figures_folder /f'{subsession_name}_{team}_driver_2_bar_graph', transparent=True)
        plt.close()

def show_driver_quali_dif_per_lap(team, team_drivers, quali_session, circuit_info, subsession_name, team_color, team_color_2, figures_folder):
    """
    Plots the delta time between two drivers across the lap.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        circuit_info (fastf1.core.Circuit): Information about the circuit.
        subsession_name (str): Name of the subsession (e.g., 'Q1', 'Q2', 'Q3').
        team_color (str): Hex color code for the first team driver.
        team_color_2 (str): Hex color code for the second team driver.
    """
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

    if driver_1_lap is not None and driver_2_lap is not None:
        delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(driver_1_lap, driver_2_lap)
        max_delta = max(abs(min(delta_time)), abs(max(delta_time))) + 0.1
        ax.vlines(x=circuit_info.corners['Distance'], ymin=-max_delta, ymax=max_delta, colors='white',
                  linestyle='dotted')
        plt.axhline(y=0, color=team_color_2, linewidth=3)
        ax.plot(ref_tel['Distance'], delta_time, color=team_color, linewidth=3)

        delta_time_at_corner = [0]
        for idx_corner, corner in circuit_info.corners.iterrows():
            for idx_dist, dist in ref_tel['Distance'].items():
                if dist > corner['Distance']:
                    delta_time_at_corner.append(round(delta_time[idx_dist], 3))
                    break
        delta_time_at_corner.append(round(delta_time.iloc[-1], 3))
    
    minor_xticks = np.arange(0, max(ref_tel['Distance']), max(ref_tel['Distance'])/100)
    minor_yticks = np.arange(-max_delta, max_delta, (max_delta)/6)
    ax.set_xticks(minor_xticks, minor=True, labels=None)
    ax.set_yticks(minor_yticks, minor=True, labels=None)
    ax.grid(which='minor', alpha=0.1)
    
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        labelleft=False,
        labelbottom=False)
    plt.ylim(-max_delta, max_delta)
    plt.xlim(0, max(ref_tel['Distance']))

    plt.xlim(0, max(ref_tel['Distance']))
    fig.tight_layout()
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = False
    plt.savefig(fname=figures_folder /  f'{subsession_name}_{team}_deltatime', transparent=True)
    plt.close(fig)

def show_fastest_lap_per_quali_session(team, team_drivers, quali_session, circuit_info, subsession_name, team_color, team_color_2, figures_folder):
    """
    Plots the speed profile of the fastest lap for each driver.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        quali_session (fastf1.core.Session): The qualifying session data.
        circuit_info (fastf1.core.Circuit): Information about the circuit.
        subsession_name (str): Name of the subsession (e.g., 'Q1', 'Q2', 'Q3').
        team_color (str): Hex color code for the first team driver.
        team_color_2 (str): Hex color code for the second team driver.
    """
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

    if driver_1_lap is not None:
        car_data = driver_1_lap.get_car_data().add_distance()
        v_min = car_data['Speed'].min()
        v_max = car_data['Speed'].max()

        for driver in team_drivers:
            driver_lap = quali_session.pick_drivers(driver).pick_fastest()
            if driver_lap is not None:
                driver_tel = driver_lap.get_car_data().add_distance()
                for _, corner in circuit_info.corners.iterrows():
                    txt = f"{corner['Number']}{corner['Letter']}"
                    ax.text(corner['Distance'], v_min - (v_min * 0.4), txt,
                            va='center_baseline', ha='center', size='xx-large')

                if driver == team_drivers[0]:
                    ax.vlines(x=circuit_info.corners['Distance'], ymin=-v_min - 20, ymax=v_max + 30, colors='white',
                              linestyle='dotted')
                    ax.plot(driver_tel['Distance'], driver_tel['Speed'], color=team_color, linewidth=3)
                else:
                    ax.plot(driver_tel['Distance'], driver_tel['Speed'], color=team_color_2, linewidth=3)

        minor_xticks = np.arange(0, max(car_data['Distance']), max(car_data['Distance']) / 100)
        minor_yticks = np.arange(v_min - 20, v_max + 20, (v_max + 20) / 30)
        ax.set_ylim([v_min - 20, v_max + 20])
        ax.set_xticks(minor_xticks, minor=True, labels=None)
        ax.set_yticks(minor_yticks, minor=True, labels=None)
        ax.grid(which='minor', alpha=0.1)
        plt.xlim(0, max(car_data['Distance']))

        fig.tight_layout()
        plt.rcParams['axes.spines.left'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.bottom'] = False
        plt.savefig(fname= figures_folder / f'{subsession_name}_{team}_speed', transparent=True)
        plt.close(fig)
