import streamlit as st
import components.dashboard_charts as dashboard_chart
import components.race_recap_charts as race_recap_chart

def render_dashboard(session, session_laps, year, race_number, race_session, Lap_Number, minute, team, team_drivers, quali, height):
    col_row_1 = st.columns((3, 0.5, 2, 2), gap='small')
    col_row_2 = st.columns((1.6, 1.6 , 4), gap='small')
    col_row_3 = st.columns((1.5, 1, 1, 1 ,1 , 1), gap='small', vertical_alignment='center')
    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_1[0]:
        dashboard_chart.get_last_laps(session, session_laps, race_session, Lap_Number, quali, height)
    with col_row_1[1]:
        dashboard_chart.get_track_status(session, session_laps, Lap_Number, height)
    with col_row_1[2]:
        dashboard_chart.get_last_laps_per_driver(session, session_laps, Lap_Number, team_drivers[0], height)
    with col_row_1[3]:
        dashboard_chart.get_last_laps_per_driver(session, session_laps, Lap_Number, team_drivers[1], height)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_2[0]:
        dashboard_chart.get_team_radio_chart(session, year, race_number, height)
    with col_row_2[1]:
        dashboard_chart.get_weather_info(session, session_laps, Lap_Number, height)
    with col_row_2[1]:
        dashboard_chart.get_race_control_message(session, race_session, Lap_Number, height)
    with col_row_2[2]:
        dashboard_chart.get_lap_and_tyre(session, session_laps, Lap_Number, height)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_3[0]:
        dashboard_chart.get_map(session, session_laps, race_session, Lap_Number, minute, height) 
    with col_row_3[1]:
        dashboard_chart.get_best(session, session_laps, Lap_Number, 'Sector1', 'Sector1Time', 's', height)
    with col_row_3[2]:
        dashboard_chart.get_best(session, session_laps, Lap_Number, 'Sector2', 'Sector2Time', 's', height)
    with col_row_3[3]:
        dashboard_chart.get_best(session, session_laps, Lap_Number, 'Sector3', 'Sector3Time', 's', height)
    with col_row_3[4]:
        dashboard_chart.get_best(session, session_laps, Lap_Number, 'LapTime', 'LapTime', 'm', height)
    with col_row_3[5]:
        dashboard_chart.get_best(session, session_laps, Lap_Number, 'TheoraticalBest', 'TheoraticalBest', 'm', height)
    st.markdown('</div>', unsafe_allow_html=True)

def render_home():
    st.title("🏁 F1 2025 Data Analysis Project")

    st.markdown("""
    ## 📊 Overview

    Welcome to the **F1 Data Analysis Dashboard**.  
    This project focuses on the **2025 Formula 1 season**, with a particular emphasis on analyzing **qualifying sessions** and **comparing teammate performance**.

    The main objective is to use telemetry and timing data to generate meaningful insights, such as:
    - Lap time differences
    - Speed profiles
    - Sector and corner performance
    - Throttle and braking behavior
    - Strategy comparisons

    ---

    ## 🚧 Project Status

    ⚠️ This project is **still under active development**. The current focus is on:
    - Processing and cleaning raw F1 session data using the `fastf1` library
    - Generating core visualizations and reports
    - Structuring the backend logic

    The **front-end interface is kept simple** for now to prioritize data accuracy and workflow automation.

    ---

    ## 🔍 Analysis Features (Work in Progress)

    ### 🏎️ Qualifying Sessions
    - Teammate lap time and sector time comparison
    - Delta time visualization (time gained/lost throughout the lap)
    - Speed profile overlays
    - Corner-by-corner dominance analysis
    - Throttle, brake, and cornering bar charts
    - Speed trap analysis

    ### 🏁 Race Sessions
    - Lap time trends and scatterplots
    - Pace and tyre strategy comparisons
    - Pit stop timing and fastest lap detection
    - Final gap and average performance stats

    Reports and plots are generated and saved as PNG, CSV, and JPEG files for each session.

    ---

    ## 🚀 Coming Soon

    - Interactive session recaps and filtering
    - Driver comparison dashboard
    - Practice session analysis
    - UI enhancements (charts, team logos, smooth layout)

    ---

    ## 🙋‍♂️ Author

    **Cyril Leconte**  
    📍 Créteil, France  
    📧 cyril.leonte07@gmail.com  
    🔗 [LinkedIn](https://linkedin.com/in/cyril-leconte-1b0742217/)  
    💻 [GitHub](https://github.com/Kuriiios)

    """)

def render_race_recap(session, session_laps, year, race_number, race_session, Lap_Number, minute, team, team_drivers, quali, height):
    col_row_1 = st.columns((1, 4, 1), gap='small')
    col_row_2 = st.columns((1, 4, 1), gap='small')
    col_row_3 = st.columns((1, 4, 1), gap='small', vertical_alignment='center')
    col_row_4 = st.columns((1, 4, 1), gap='small', vertical_alignment='center')
    with col_row_1[0]:
        race_recap_chart.show_pace_comp(team, session, team_drivers[0], height)
    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_1[1]:
        race_recap_chart.show_laptime_scatterplot(team, team_drivers, session, height)
    st.markdown('</div>', unsafe_allow_html=True)
    with col_row_1[2]:
        race_recap_chart.show_pace_comp(team, session, team_drivers[1], height)
    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_1[1]:
        race_recap_chart.show_laptime_comp(team, session, height)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-row">', unsafe_allow_html=True)
    with col_row_1[1]:
        race_recap_chart.show_tyre_strategy(team, team_drivers, session, height)
    st.markdown('</div>', unsafe_allow_html=True)
