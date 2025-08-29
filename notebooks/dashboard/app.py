import streamlit as st
from logic.pages_logic import render_home
from logic.sidebar import render_sidebar

st.set_page_config(
    page_title='F1 Analysis',
    page_icon='🏁🏎️',
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .scrollable-container {
        max-height: 80vh; /* Limit height to 80% of viewport */
        overflow-y: auto; /* Enable vertical scroll inside the box */
        padding-right: 1rem; /* Avoid scrollbar overlap */
    }
    .main {
        max-width: 1400px; /* Optional: Limit total page width */
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    state = render_sidebar()

render_home()

st.markdown('</div>', unsafe_allow_html=True)