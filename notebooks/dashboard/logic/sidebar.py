import streamlit as st
import numpy as np
import fastf1.plotting

from logic.transform import event_format
from data.fetch_data import get_session
from logic.transform import quali_session_range

def compute_chart_height(compact_pct: int, preset: str, rows=3, header_px=120, footer_px=40, min_height=120, base_height=250):
    if preset == "Auto":
        return max(min_height, int(base_height * compact_pct / 100))
    mapping = {"Laptop 900px": 900, "Desktop 1080px": 1080, "Large 1440px": 1440}
    vp = mapping.get(preset, 1080)
    available = max(480, vp - header_px - footer_px)
    per_row = int(available / rows)
    return max(min_height, int(per_row * compact_pct / 100))

def render_sidebar():

    st.sidebar.header("Layout / Fit-to-screen")

    compactness = st.sidebar.slider(
        "Compactness (%) — lower = smaller charts",
        min_value=60, max_value=140, value=100, step=5
    )

    screen_preset = st.sidebar.selectbox(
        "Screen preset (for auto-fit)",
        ("Auto", "Laptop 900px", "Desktop 1080px", "Large 1440px")
    )
    
    height = compute_chart_height(compactness, screen_preset)

    st.title('🏁🏎️ F1 Analysis')

    year_list = [2023, 2024, 2025]
    year = st.selectbox('Select a year', year_list, index=len(year_list) - 1)

    race_list = list(range(1, 25))
    race_number = st.selectbox('Select a race', race_list, index=12)

    event = event_format(year, race_number)
    session_list = {
        'conventional': ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race'],
        'sprint_qualifying': ['Practice 1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']
    }[event]

    race_session = st.selectbox('Select a session', session_list, index=len(session_list) - 1)
    session = get_session(year, race_number, race_session)

    session_laps = session.laps
    Lap_Number = 10
    minute = 60
    quali = 'none'

    teams = fastf1.plotting.list_team_names(session)
    team = st.selectbox('Select a team', teams, index=4)
    team_drivers = fastf1.plotting.get_driver_abbreviations_by_team(team, session=session)

    max_lap = int(max(session_laps.LapNumber)) + 1

    if race_session in ['Race', 'Sprint']:
        lap_list = list(range(1, max_lap))
        Lap_Number = st.selectbox('Select a lap', lap_list, index=len(lap_list) - 1)

    elif race_session in ['Qualifying', 'Sprint Qualifying']:
        q1, q2, q3 = session_laps.split_qualifying_sessions()
        q_dict = {
            'Q1': q1[~np.isnat(q1['LapTime'])],
            'Q2': q2[~np.isnat(q2['LapTime'])],
            'Q3': q3[~np.isnat(q3['LapTime'])]
        }

        quali_list = ['Q1', 'Q2', 'Q3']
        quali = st.selectbox('Select a quali session', quali_list, index=1)
        session_laps = q_dict[quali]
        minute_list = quali_session_range(session_laps)
        minute = st.selectbox('Select a minute', minute_list, index=len(minute_list) - 1)

    elif race_session.startswith('Practice'):
        minute_list = list(range(0, 61))
        minute = st.selectbox('Select a minute', minute_list, index=len(minute_list) - 1)

    return session, session_laps, year, race_number, race_session, Lap_Number, minute, team, team_drivers, quali, height