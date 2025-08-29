import streamlit as st
from logic.sidebar import render_sidebar 
from logic.pages_logic import render_race_recap

st.set_page_config(
    page_title='F1 Dashboard',
    page_icon='🏎️',
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    state = render_sidebar()

render_race_recap(*state)