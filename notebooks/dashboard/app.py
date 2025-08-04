import streamlit as st
import numpy as np
import fastf1
import fastf1.plotting

from pages.dashboard import render_dashboard
from logic.transform import event_format
from data.fetch_data import get_session

st.set_page_config(
    page_title='F1 Analysis',
    page_icon='🏁🏎️',
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title('🏁🏎️ F1 Analysis')
    
    year_list = [2023, 2024, 2025]
    year = st.selectbox('Select a year', year_list, index=len(year_list)-1)

    race_list = list(range(1,25))
    race_number = st.selectbox('Select a race', race_list, index=12)

    if event_format(year, race_number) == 'conventional':
        session_list = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race']
        race_session = st.selectbox('Select a session', session_list, index=len(session_list)-1)
        session = get_session(year, race_number, race_session)

    elif event_format(year, race_number) == 'sprint_qualifying':
        session_list = ['Practice 1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']
        race_session = st.selectbox('Select a session', session_list, index=len(session_list)-1)    
        session = get_session(year, race_number, race_session)
    
    Lap_Number= 10
    minute = 60
    quali= 'none'

    teams = fastf1.plotting.list_team_names(session)
    team = st.selectbox('Select a team', teams, index=4)
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)
    
    max_lap = int(max(session.laps.LapNumber))+1
    if race_session == 'Race' or race_session == 'Sprint':
        lap_list = list(range(1, max_lap))
        Lap_Number = st.selectbox('Select a lap', lap_list, index=len(lap_list)-1)
    elif race_session == 'Qualifying' or race_session == 'Sprint Qualifying':          
        quali_list = ['Q1', 'Q2', 'Q3']
        quali = st.selectbox('Select a quali session', quali_list, index=0)

        minute_list = list(range(0, 61))
        minute = st.selectbox('Select a minute', minute_list, index=10)
    elif race_session == 'Practice 1' or race_session == 'Practice 2' or race_session == 'Practice 3':

        minute_list = list(range(0, 61))
        minute = st.selectbox('Select a minute', minute_list, index=len(minute_list)-1)
    
render_dashboard(session, year, race_number, race_session, Lap_Number, minute, team_drivers, quali)