import streamlit as st
import altair as alt
import data.fetch_data as dt
import numpy as np
import pandas as pd
import os
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator
import io
import base64
import fastf1
import fastf1.plotting
import fastf1.api
import matplotlib.pyplot as plt
from datetime import timedelta
import utils.race_recap_format as fmt
import data.fetch_data as dt

def show_tyre_strategy(team, team_drivers,session, height):
    driver_1_laps, driver_2_laps = fmt.fixed_nat_all_laps(team, session)
    fig, ax = plt.subplots(figsize=(15, 2.5), facecolor='none')
    ax.set_facecolor('none')

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
    ax.tick_params(colors='white')
    plt.grid(False)
    plt.grid(color='w', which='major', axis='x', linestyle='dotted')

    ax.xaxis.tick_top()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xlim([0, last_lap])
    
    st.pyplot(fig)


def show_pace_comp(team, session, driver, height):
    lap_times = session.laps.pick_drivers(driver).pick_quicklaps(1.17).reset_index()

    plt.rcParams.update({
        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': False,
        'font.size': 12
    })

    fig, ax = plt.subplots(figsize=(2.5, 3), facecolor='none')
    ax.set_facecolor('none')
    if "LapTime" in lap_times.columns and lap_times["LapTime"].dropna().size > 0:
        lap_times["LapTimeSeconds"] = lap_times["LapTime"].dt.total_seconds()
        sns.boxplot(
            data=lap_times,
            y="LapTimeSeconds",
            color= fastf1.plotting.get_driver_color(driver, session=session),
            linecolor='white',
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(axis='y', colors='white', which='both', left=True, bottom=False, labelleft=True)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt.seconds_to_mmss))

    plt.xticks(visible=False)
    plt.grid(color='w', which='major', axis='y', linestyle='dotted')
    plt.tight_layout()
    st.pyplot(fig)

def show_laptime_scatterplot(team, team_drivers, session, height):
    driver_1_laps, driver_2_laps = fmt.fixed_nat_fast_laps(team, session)
    driver_1_laps = pd.DataFrame(driver_1_laps)
    driver_2_laps = pd.DataFrame(driver_2_laps)
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)

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
    
    fig, ax = plt.subplots(figsize=(15, 4), facecolor='none')
    ax.set_facecolor('none')
    
    palette = fastf1.plotting.get_compound_mapping(session=session)
    palette['nan'] = palette['UNKNOWN']
    palette['nan'] = '#00ffff'
    
    if driver_1_laps.empty:
        driver_1_laps.loc[0] = 0.0
        driver_1_laps['DriverNumber'] = team_drivers[0]
        driver_1_laps['LapNumber'] = 0.0
        driver_1_laps['LapTime'] = pd.Timestamp('NaT').to_pydatetime()
        driver_1_laps['Compound'] = 'UNKNOWN'
    
    if driver_2_laps.empty:
        driver_2_laps.loc[0] = 0
        driver_2_laps['DriverNumber'] = team_drivers[1]
        driver_2_laps['LapNumber'] = 0.0
        driver_2_laps['LapTime'] = pd.Timestamp('NaT').to_pydatetime()
        driver_2_laps['Compound'] = 'UNKNOWN'
    

    if not driver_1_laps.empty:
        sns.scatterplot(data=driver_1_laps,
                        x="LapNumber",
                        y="LapTime",
                        hue = 'Compound',
                        palette=palette,
                        marker='s',
                        edgecolor = 'black',
                        s=50,
                        linewidth=1)

    if not driver_2_laps.empty:
        sns.scatterplot(data=driver_2_laps,
                        x="LapNumber",
                        y="LapTime",
                        hue = 'Compound',
                        palette=palette,
                        marker='D',
                        edgecolor = 'black',
                        s=50,
                        linewidth=1)
    
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt.microseconds_to_mmss))
    ax.invert_yaxis()
    ax.set_xlim([0, last_lap])
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(colors='white')
    ax.get_legend().remove()


    plt.grid(color='w', which='major', axis='both', linestyle='dotted')
    plt.tight_layout()
    st.pyplot(fig)


def show_laptime_comp(team, session, height):
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    driver_1_laps, driver_2_laps = fmt.fixed_nat_all_laps(team, session)
    last_lap = int(max(session.laps['LapNumber']))

    fig, ax = plt.subplots(figsize=(15, 4), facecolor='none')
    ax.set_facecolor('none')

    if not driver_1_laps.empty:
        ax.plot(driver_1_laps['LapNumber'], driver_1_laps['LapTime'],
                color=fastf1.plotting.get_driver_color(team_drivers[0], session=session),
                label=team_drivers[0])
    if not driver_2_laps.empty: 
        ax.plot(driver_2_laps['LapNumber'], driver_2_laps['LapTime'],
                color=fastf1.plotting.get_driver_color(team_drivers[1], session=session),
                label=team_drivers[1])

    ax.tick_params(labelright=True, colors='white',)
    ax.set_xlim([0, last_lap])
    ax.yaxis.set_major_formatter(FuncFormatter(fmt.microseconds_to_mmss))
    plt.tick_params(bottom=False, top=False, labelbottom=False,  colors='white')
    plt.grid(color='w', which='major', axis='both', linestyle='dotted')
    ax.legend(frameon=False)
    ax.get_legend().remove()

    st.pyplot(fig, height=height)

