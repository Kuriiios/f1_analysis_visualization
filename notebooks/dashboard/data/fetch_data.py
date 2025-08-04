import pandas as pd
import streamlit as st
import fastf1
from pathlib import Path

parent_file = Path(__file__).resolve().parent.parent.parent.parent
save_folder_transcription = '/data_dashboard/'
save_path = str(parent_file) + save_folder_transcription

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

@st.cache_data(ttl=3600)
def get_session(year, race_number, race_session):
    session= fastf1.get_session(year, race_number, race_session)
    session.load()
    return session

def get_team_radio(session, year, race_number):
    team_radio_df = pd.read_csv(filepath_or_buffer = (str(save_path) + str(session.event.Session5Date)[:10]+'_'+str(session.event.EventName).replace(' ','_')+'.csv'), index_col=0)
    return team_radio_df