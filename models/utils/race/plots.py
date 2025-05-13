import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import seaborn as sns
import fastf1
import fastf1.plotting
from datetime import timedelta
import os
import pandas as pd
import numpy as np
import sys

def fixed_nat_all_laps(team, session):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_laps(range(0, (int(max(session.laps['LapNumber'])) + 1))).reset_index()
    if not driver_1_laps.empty:
        laptime_counter_driver_1 = 0
        for lap in driver_1_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_1_laps.loc[laptime_counter_driver_1, 'LapTime'] = driver_1_laps.loc[laptime_counter_driver_1 +1, 'LapStartTime'] - driver_1_laps.loc[laptime_counter_driver_1, 'LapStartTime']
                laptime_counter_driver_1 +=1
            except KeyError:
                break

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
    
    driver_1_laps = session.laps.pick_drivers(team_drivers[0]).pick_quicklaps(1.17).reset_index()
    driver_2_laps = session.laps.pick_drivers(team_drivers[1]).pick_quicklaps(1.17).reset_index()
    if not driver_1_laps.empty:
        laptime_counter_driver_1 = 0
        for lap in driver_1_laps['LapTime']:
            try:
                if 'NaT' in str(lap):
                    driver_1_laps.loc[laptime_counter_driver_1, 'LapTime'] = driver_1_laps.loc[laptime_counter_driver_1 +1, 'LapStartTime'] - driver_1_laps.loc[laptime_counter_driver_1, 'LapStartTime']
                laptime_counter_driver_1 +=1
            except KeyError:
                break

    laptime_counter_driver_2 = 0
    for lap in driver_2_laps['LapTime']:
        try:
            if 'NaT' in str(lap):
                driver_2_laps.loc[laptime_counter_driver_2, 'LapTime'] = driver_2_laps.loc[laptime_counter_driver_2 +1, 'LapStartTime'] - driver_2_laps.loc[laptime_counter_driver_2, 'LapStartTime']
            laptime_counter_driver_2 +=1
        except KeyError:
            break
    return driver_1_laps, driver_2_laps


def seconds_to_mmss(x, pos):
    """
    Formatter function to convert seconds to minutes:seconds.milliseconds format.

    Args:
        x (float): Time in seconds.
        pos (int): The tick position (not used, required by FuncFormatter).

    Returns:
        str: Formatted time string (MM:SS.ms).
    """
    try:
        # x is a float in days → convert to timedelta
        td = timedelta(days=x)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02}"
    except Exception as e:
        return "0:00"

def show_laptime_comp(team, session, team_color, team_color_2, figures_folder):
    """
    Plots the lap time comparison between two drivers of a team across the session.

    Args:
        team_drivers (list): List of driver abbreviations for the team.
        session (fastf1.core.Session): The session data.
        team_color (str): The primary color for the team.
        team_color_2 (str): The secondary color for the team.
        figures_folder (str): Path to the directory where figures are saved.
    """
    driver_1_laps, driver_2_laps = fixed_nat_all_laps(team, session)
    last_lap = int(max(session.laps['LapNumber']))

    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(driver_1_laps['LapNumber'], driver_1_laps['LapTime'], color=team_color)
    ax.plot(driver_2_laps['LapNumber'], driver_2_laps['LapTime'], color=team_color_2)
    ax.tick_params(labelright=True)
    ax.set_xlim([0, last_lap])
    ax.yaxis.set_major_formatter(FuncFormatter(seconds_to_mmss))

    plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)
    
    plt.grid(color='w', which='major', axis='both', linestyle='dotted')
    plt.savefig(fname= os.path.join(figures_folder, f'{session.name}_{team}_laptime_comp.png'), transparent=True)
    plt.close(fig)
    
def show_laptime_scatterplot(team, team_drivers, session, team_color, team_color_2, figures_folder):
    """
    Plots the lap time scatterplot for two drivers, colored by tyre compound.

    Args:
        team_drivers (list): List of driver abbreviations.
        session (fastf1.core.Session): Session data.
        team_color (str): Primary team color.
        team_color_2 (str): Secondary team color.
        figures_folder (str): Directory to save the plot.
    """
    driver_1_laps, driver_2_laps = fixed_nat_fast_laps(team, session)
    
    if driver_1_laps.empty and driver_2_laps.empty:
        print("No valid lap times to display.")
        return
    elif driver_1_laps.empty:
        min_laptime = min(driver_2_laps['LapTime'])
        max_laptime = max(driver_2_laps['LapTime'])
    elif driver_2_laps.empty:
        min_laptime = min(driver_1_laps['LapTime'])
        max_laptime = max(driver_1_laps['LapTime'])
    else:
        min_laptime = min(min(driver_1_laps['LapTime']), min(driver_2_laps['LapTime']))
        max_laptime = max(max(driver_1_laps['LapTime']), max(driver_2_laps['LapTime']))

    min_laptime = min_laptime - timedelta(seconds= 1)
    max_laptime = max_laptime + timedelta(seconds= 1)

    last_lap = int(max(session.laps['LapNumber'])) + 1
    
    fig, ax = plt.subplots(figsize=(5.75, 4.2))
    
    palette = fastf1.plotting.get_compound_mapping(session=session)
    palette['nan'] = palette['UNKNOWN']
    palette['nan'] = '#00ffff'
    
    if driver_1_laps.empty:
        driver_1_laps.loc[0] = 0.0
        driver_1_laps['DriverNumber'] = team_drivers[0]
        driver_1_laps['LapNumber'] = 0.0
        driver_1_laps['LapTime'] = pd.Timestamp('NaT').to_pydatetime()
        driver_1_laps['Compound'] = 'UNKNOWN'
    '''
    if driver_2_laps.empty:
        driver_2_laps.loc[0] = 0
        driver_2_laps['DriverNumber'] = team_drivers[1]
        driver_2_laps['LapNumber'] = 0.0
        driver_2_laps['LapTime'] = pd.Timestamp('NaT').to_pydatetime()
        driver_2_laps['Compound'] = 'UNKNOWN'
    '''
    sns.scatterplot(data=driver_1_laps,
                    x="LapNumber",
                    y="LapTime",
                    hue = 'Compound',
                    palette=palette,
                    edgecolor = team_color,
                    style="Compound",
                    s=50,
                    linewidth=0.5)

    sns.scatterplot(data=driver_2_laps,
                    x="LapNumber",
                    y="LapTime",
                    hue = 'Compound',
                    palette=palette,
                    edgecolor = team_color_2,
                    style="Compound",
                    s=50,
                    linewidth=0.5)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.invert_yaxis()
    ax.tick_params(labelleft=False)
    ax.set_xlim([0, last_lap])
    ax.set(xlabel=None, ylabel=None)
    ax.set_ylim([min_laptime, max_laptime])

    plt.tick_params(left = False)
    plt.tick_params(bottom = False)
    plt.legend(frameon=False)
    plt.grid(color='w', which='major', axis='both', linestyle='dotted')

    plt.tight_layout()
    plt.savefig(fname = os.path.join(figures_folder, f'{session.name}_{team}_laptime_scatterplot.png'), transparent=True)
    plt.close(fig)

def show_pace_comp(team, session, team_color, team_color_2, figures_folder):
    """
    Plots the pace comparison (boxplot) of two drivers.

    Args:
        team_drivers (list): Driver abbreviations.
        session (fastf1.core.Session): Session data.
        team_color (str): Primary team color.
        team_color_2 (str): Secondary team color.
        figures_folder (str): Directory to save plots.
    """
    driver_1_laps, driver_2_laps = fixed_nat_fast_laps(team, session)

    if driver_1_laps.empty and driver_2_laps.empty:
        print("No valid lap times to display.")
        return
    elif driver_1_laps.empty:
        min_laptime = min(driver_2_laps['LapTime'])
        max_laptime = max(driver_2_laps['LapTime'])
    elif driver_2_laps.empty:
        min_laptime = min(driver_1_laps['LapTime'])
        max_laptime = max(driver_1_laps['LapTime'])
    else:
        min_laptime = min(min(driver_1_laps['LapTime']), min(driver_2_laps['LapTime']))
        max_laptime = max(max(driver_1_laps['LapTime']), max(driver_2_laps['LapTime']))

    min_laptime = (min_laptime - timedelta(seconds= 1))
    max_laptime = (max_laptime + timedelta(seconds= 1))

    plt.rcParams.update({
        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': False,
        'font.size': 12
    })

    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    if "LapTime" in driver_1_laps.columns and driver_1_laps["LapTime"].dropna().size > 0:
        sns.boxplot(
            data=driver_1_laps,
            y="LapTime",
            color=team_color,
            linecolor='white',
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )

    ax.set_ylim([max_laptime, min_laptime])
    ax.invert_yaxis()
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(bottom=False)
    ax.tick_params(axis='y', which='both', left=True, labelleft=True)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_formatter(FuncFormatter(seconds_to_mmss))

    plt.xticks(visible=False)
    plt.grid(color='w', which='major', axis='y', linestyle='dotted')
    plt.tight_layout()
    plt.savefig(fname= os.path.join(figures_folder, f'{session.name}_{team}_driver_1_pace.png'), transparent=True)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(2.5, 4.2))
    if "LapTime" in driver_2_laps.columns and driver_2_laps["LapTime"].dropna().size > 0:
        sns.boxplot(
            data=driver_2_laps,
            y="LapTime",
            color=team_color_2,
            linecolor='white',
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )

    ax.set_ylim([max_laptime, min_laptime])
    ax.invert_yaxis()
    ax.set(xlabel=None, ylabel=None)
    ax.yaxis.tick_right()
    ax.tick_params(bottom=False)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_formatter(FuncFormatter(seconds_to_mmss))

    plt.xticks(visible=False)
    plt.grid(color='w', which='major', axis='y', linestyle='dotted')
    plt.tight_layout()
    plt.savefig(fname= os.path.join(figures_folder, f'{session.name}_{team}_driver_2_pace.png'), transparent=True)
    plt.close(fig)
    
def show_tyre_strategy(team, team_drivers,session, figures_folder):
    """
    Plots the tyre strategy used by each driver of a team.

    Args:
        team_drivers (list): List of driver abbreviations.
        session (fastf1.core.Session): Session data.
        figures_folder (str): Directory to save the plot.
    """
    driver_1_laps, driver_2_laps = fixed_nat_all_laps(team, session)
    fig, ax = plt.subplots(figsize=(9.2, 1.2))

    if len(driver_1_laps) > 1 :
        driver_1_laps.loc[0, 'LapTime'] = driver_1_laps.loc[1, 'LapStartTime'] - driver_1_laps.loc[0, 'LapStartTime']
    if len(driver_2_laps)>1:
        driver_2_laps.loc[0, 'LapTime'] = driver_2_laps.loc[1, 'LapStartTime'] - driver_2_laps.loc[0, 'LapStartTime']
    last_lap = int(max(session.laps['LapNumber']))
    
    for driver in team_drivers:
        laps = session.laps.pick_drivers(driver)
        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"],
                                                                session=session)
            plt.barh(
                y=driver,
                width=row["StintLength"],
                height = 0.4,
                align='center',
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black",
                fill=True
            )

            previous_stint_end += row["StintLength"]

    plt.grid(False)
    plt.grid(color='w', which='major', axis='x', linestyle='dotted')

    ax.xaxis.tick_top()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xlim([0, last_lap])

    plt.tight_layout()
    plt.savefig(fname= os.path.join(figures_folder, f'{session.name}_{team}_tyre_strategy.png'), transparent=True)
    plt.close(fig)
