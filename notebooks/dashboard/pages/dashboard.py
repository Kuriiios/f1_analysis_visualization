import streamlit as st
import components.charts as chart

def render_dashboard(session, year, race_number, race_session, Lap_Number, minute, team_drivers, quali):
    col_row_1 = st.columns((3, 0.5, 2, 2), gap='small')
    col_row_2 = st.columns((1.6, 1.6 , 4), gap='small')
    col_row_3 = st.columns((1.5, 1, 1, 1 ,1 , 1), gap='small', vertical_alignment='center')
    with col_row_1[0]:
        chart.get_last_laps(session, race_session, Lap_Number, quali)
    with col_row_1[1]:
        chart.get_track_status(session, Lap_Number)
    with col_row_1[2]:
        chart.get_last_laps_per_driver(session, Lap_Number, team_drivers[0])
    with col_row_1[3]:
        chart.get_last_laps_per_driver(session, Lap_Number, team_drivers[1])
    with col_row_2[0]:
        chart.get_team_radio_chart(session, year, race_number)
    with col_row_2[1]:
        chart.get_weather_info(session, Lap_Number)
    with col_row_2[1]:
        chart.get_race_control_message(session, race_session, Lap_Number)
    with col_row_2[2]:
        chart.get_lap_and_tyre(session, Lap_Number)
    with col_row_3[0]:
        chart.get_map(session, Lap_Number) 
    with col_row_3[1]:
        chart.get_best(session, Lap_Number, 'Sector1', 'Sector1Time', 's')
    with col_row_3[2]:
        chart.get_best(session, Lap_Number, 'Sector2', 'Sector2Time', 's')
    with col_row_3[3]:
        chart.get_best(session, Lap_Number, 'Sector3', 'Sector3Time', 's')
    with col_row_3[4]:
        chart.get_best(session, Lap_Number, 'LapTime', 'LapTime', 'm')
    with col_row_3[5]:
        chart.get_best(session, Lap_Number, 'TheoraticalBest', 'TheoraticalBest', 'm')