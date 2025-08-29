import fastf1
import pandas as pd 
import json
import datetime
import numpy as np
from sqlalchemy import UniqueConstraint, create_engine, select, insert, and_, Column, Integer, SmallInteger, String, Float, MetaData, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import sqlalchemy as sa

with open('log.json', 'r') as file:
    data = json.load(file)

DATABASE_URL = data.get('database_url')
#SEASON = int(input("Enter year: "))
#ROUND = int(input("Enter round: "))
SEASON = 2025
ROUND = 1

engine = create_engine(DATABASE_URL, echo=True)

team_info = {
    "Ferrari":["Ferrari", "FER", "#e80020"],
    "McLaren":["McLaren", "MCL", "#ff8000"],
    "Red Bull Racing":["Red Bull Racing", "RBR", "#0600ef"],
    "Alpine":["Alpine", "ALP", "#ff87bc"],
    "Mercedes":["Mercedes", "MER", "#27f4d2"],
    "Aston Martin":["Aston Martin", "AMR", "#00665e"],
    "Racing Bulls":["Racing Bulls", "RBS", "#fcd700"],
    "Williams":["Williams", "WIL", "#00a0dd"],
    "Kick Sauber":["Sauber", "SAU", "#00e700"],
    "Haas F1 Team":["Haas", "HAA", "#b6babd"],
}

drivers_info = {
    1: [1, "VER", "Max Verstappen", "#FF6600", "NL"],
    30: [30, "LAW", "Liam Lawson", "#FFCC01", "NZ"],
    10: [10, "GAS", "Pierre Gasly", "#08143b", "FR"],
    7: [7, "DOO", "Jack Doohan", "#ff0063", "AU"],
    43: [43, "COL", "Franco Colapinto", "#3576ae", "AR"],
    12: [12, "ANT", "Kimi Antonelli", "#0ad95d", "IT"],
    63: [63, "RUS", "George Russell", "#00a3e3", "UK"],
    14: [14, "ALO", "Fernando Alonso", "#00a4e7", "ES"],
    18: [18, "STR", "Lance Stroll", "#00665e", "CA"],
    16: [16, "LEC", "Charles Leclerc", "#e1022d", "MC"],
    44: [44, "HAM", "Lewis Hamilton", "#7a25f0", "UK"],
    22: [22, "TSU", "Yuki Tsunoda", "#fd8b35", "JP"],
    6: [6, "HAD", "Isack Hadjar", "#0023d1", "FR"],
    23: [23, "ALB", "Alexander Albon", "#0023d1", "TH"],
    55: [55, "SAI", "Carlos Sainz", "#da291c", "ES"],
    27: [27, "HUL", "Nico Hulkenberg", "#181c25", "DE"],
    5: [5, "BOR", "Gabriel Bortoleto", "#a5cd39", "BR"],
    31: [31, "OCO", "Esteban Ocon", "#f10000", "FR"],
    87: [87, "BEA", "Ollie Bearman", "#fff200", "UK"],
    4: [4, "NOR", "Lando Norris", "#d2ff00", "UK"],
    81: [81, "PIA", "Oscar Piastri", "#0e1f66", "AU"],
}

tyre_allocation = {
    1 : [5, 4, 3],
    2 : [4, 3, 2],
    3 : [3, 2, 1],
    4 : [3, 2, 1],
    5 : [5, 4, 3],
    6 : [5, 4, 3],
    7 : [6, 5, 4],
    8 : [6, 5, 4],
    9 : [3, 2, 1],
    10 : [6, 5, 4],
    11 : [5, 4, 3],
    12 : [4, 3, 2],
    13 : [4, 3, 1],
    14 : [5, 4, 3],
}

engine = sa.create_engine("postgresql+psycopg2://creator:roadtose@localhost:5432/f1_data", echo=True)

metadata = sa.MetaData()

metadata.reflect(bind=engine)

CarData = metadata.tables['car_data']
Compound = metadata.tables['compound']
Driver = metadata.tables['driver']
Drs = metadata.tables['drs']
Dta = metadata.tables['dta']
EventRound = metadata.tables['event-round']
Lap = metadata.tables['lap']
PosData = metadata.tables['pos_data']
Session = metadata.tables['sessions']
Team = metadata.tables['team']
TrackStatus = metadata.tables['track_status']
Weather = metadata.tables['weather']
WindDirection = metadata.tables['wind_direction']


#fastf1.Cache.enable_cache("./cache")

SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as db:
    team_map = {}
    for team_name, info in team_info.items():
        try:
            team = db.query(Team).filter(Team.team_name == info[0]).first()
            if not team:
                team = Team(
                    team_name= info[0],
                    team_abbreviation= info[1],
                    team_color= info[2],
                )
                db.add(team)
                db.flush()
            team_map[team_name] = team.team_id
        except:
            print(f"Error loading data for team {team_name}: {info}. Skipping.")
            continue

    driver_map = {}
    for driver_number, info in drivers_info.items():
        try:
            driver = db.query(Driver).filter(Driver.driver_number == info[0]).first()
            if not driver:
                driver = Driver(
                    driver_number = info[0],
                    driver_abbreviation = info[1],
                    driver_name = info[2],
                    driver_color = info[3],
                    country = info[4],
                )
                db.add(driver)
                db.flush()
            driver_map[driver_number] = driver.driver_id
        except Exception as e:
            print(f"Error loading data for driver {driver_number}: {info}. Skipping.")
            continue

    for i in range(1, 6): 
        try:
            current_session = fastf1.get_session(SEASON, ROUND, i)
            current_session.load()
        except Exception as e:
            print(f"Error loading current_session {i}: {e}. Skipping.")
            continue

        laps = current_session.laps

        try:
            event_round_event_date = pd.to_datetime(current_session.event.EventDate).to_pydatetime()
            #Add data into EventRound table
            event_round = db.query(EventRound).filter(
                and_(
                    EventRound.round_number == int(current_session.event.RoundNumber),
                    EventRound.event_name == current_session.event.EventName,
                    EventRound.event_date == event_round_event_date,
                )).first()
            if not event_round:
                tyres = tyre_allocation.get(int(current_session.event.RoundNumber), [0, 0, 0])
                event_round = EventRound(
                    #year = event_round_event_date.year,
                    round_number = int(current_session.event.RoundNumber),
                    country = current_session.event.Country,
                    location = current_session.event.Location,
                    event_name = current_session.event.EventName,
                    event_date = event_round_event_date,
                    sprint_event = current_session.event.EventFormat in ("sprint", "sprint_qualifying"),
                    soft = tyres[0],
                    medium = tyres[1],
                    hard = tyres[2],
                )
                db.add(event_round)
                db.flush()
        except Exception as e:
            print(f"Error loading data for event_round : {e}. Skipping.")
            continue   
        #Add data into Session table
        try:
            session_date = pd.to_datetime(current_session.date).to_pydatetime()
            session = db.query(Session).filter(
                and_(
                    Session.event_round_id == event_round.event_round_id,
                    Session.session_name == current_session.name,
                    Session.session_date == session_date
                )).first()
            if not session:
                session = Session(
                    event_round_id = event_round.event_round_id,
                    session_name = current_session.name,
                    session_date = session_date,
                )
                db.add(session)
                db.flush()
        except Exception as e:
            print(f"Error loading data for session : {e}. Skipping.")
            continue   
        #Add data into Weather table
        try:
            weather_df = laps.get_weather_data().replace({pd.NaT:None, np.nan:None}).copy()
            if not weather_df.empty:
                weather_df.loc[:, 'session_id'] = session.session_id
                weather_df['time_'] = pd.to_timedelta(weather_df['Time']).dt.total_seconds()
                weather_df.drop(columns=["Time"], inplace=True)
                weather_dicts = weather_df.rename(columns={
                    'AirTemp': 'air_temp', 
                    'Humidity': 'humidity', 
                    'Pressure': 'pressure', 
                    'Rainfall': 'rainfall',
                    'TrackTemp': 'track_temp', 
                    'WindDirection': 'wind_direction', 
                    'WindSpeed': 'wind_speed',
                }).to_dict(orient="records")
                print(weather_dicts)
                db.bulk_insert_mappings(Weather, weather_dicts)
        except Exception as e:
            print(f"Error loading data for weather : {e}. Skipping.")
            continue   

        for driver_number in current_session.drivers:
            driver_id = driver_map.get(int(driver_number))
            if not driver_id:
                print(f"Driver number {driver_number} not found in drivers_info. Skipping.") 
                continue

            driver_team_name = current_session.get_driver(driver_number)['TeamName']
            team_id = team_map.get(driver_team_name)
            if not team_id:
                print(f"Team {driver_team_name} not found in team_map. Skipping.")
                continue

            #Add data into DriverTeamAssignment table
            try:
                dta = db.query(Dta).filter(
                    and_(Dta.driver_id == driver_id,
                        Dta.team_id == team_id,
                        Dta.session_id == session.session_id
                        )).first()
                if not dta :
                    dta = Dta (
                        driver_id = driver_id,
                        team_id = team_id,
                        session_id = session.session_id
                    )
                    db.add(dta)
                    db.flush()
            except Exception as e:
                print(f"Error loading data for dta : {e}. Skipping.")
                continue
            #Add data into Lap table
            try:
                driver_laps = laps.pick_drivers(driver_number)
                if not driver_laps.empty:
                    driver_laps = driver_laps.replace({pd.NaT:None, np.nan:None}).copy()
                    driver_laps = driver_laps[driver_laps['LapStartDate'].apply(isinstance,args= [datetime.datetime])]

                    timedelta_cols = ['LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime', 'LapStartTime']
                    for col in timedelta_cols:
                        driver_laps.loc[:, col +'_s'] = driver_laps[col].apply(lambda x: x.total_seconds() if pd.notna(x) else None)
                    driver_laps.loc[:, 'driver_team_assignment_id'] = dta.driver_team_assignment_id
                    driver_laps.loc[:, 'LapStartDate'] = pd.to_datetime(driver_laps['LapStartDate'])
                    lap_dicts = driver_laps [['driver_team_assignment_id', 'Compound', 'LapTime_s', 'LapNumber', 'Stint',
                        'PitOutTime_s', 'PitInTime_s',
                        'Sector1Time_s', 'Sector2Time_s', 'Sector3Time_s',
                        'Sector1SessionTime_s', 'Sector2SessionTime_s', 'Sector3SessionTime_s',
                        'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
                        'IsPersonalBest', 'TyreLife', 'LapStartTime_s', 'LapStartDate',
                        'Position', 'TrackStatus', 'Deleted'
                    ]].rename(columns={
                        'Compound': 'compound', 'Stint': 'stint',
                        'LapTime_s':'laptime_s', 'LapNumber':'lap_number', 'PitOutTime_s':'pit_out_time',
                        'PitInTime_s':'pit_in_time', 'Sector1Time_s':'sector1_time', 'Sector2Time_s':'sector2_time',
                        'Sector3Time_s':'sector3_time', 'Sector1SessionTime_s':'sector1_session_time',
                        'Sector2SessionTime_s':'sector2_session_time', 'Sector3SessionTime_s':'sector3_session_time',
                        'SpeedI1': 'speed_i1', 'SpeedI2': 'speed_i2', 'SpeedFL': 'speed_fl', 'SpeedST': 'speed_st',
                        'IsPersonalBest': 'is_personal_best', 'TyreLife': 'tyre_life', 'LapStartTime_s':'lap_start_time',
                        'LapStartDate': 'lap_start_date', 'Position': 'position', 'TrackStatus': 'track_status', 'Deleted': 'deleted',
                    }).to_dict(orient='records')
                    db.bulk_insert_mappings(Lap, lap_dicts)
                    db.flush()
            except Exception as e:
                print(f"Error loading data for lap : {e}. Skipping.")
                continue
            
            lap_map = {
                row.lap_number: row.lap_id
                for row in db.query(Lap.lap_id, Lap.lap_number).filter(
                    Lap.driver_team_assignment_id == dta.driver_team_assignment_id
                ).all()
            }
            try:
                driver_laps = laps.pick_drivers(driver_number).sort_values('LapStartDate')
                driver_laps_date = driver_laps[['LapStartDate', 'LapNumber']].copy()
                driver_laps_date = driver_laps_date[driver_laps_date['LapStartDate'].apply(isinstance,args= [datetime.datetime])]
                driver_car_data = driver_laps.get_car_data().add_track_status().add_distance().add_differential_distance().add_relative_distance().add_driver_ahead()
                driver_car_data['Date'] = pd.to_datetime(driver_car_data['Date'])
                driver_car_data = driver_car_data.sort_values('Date')
                driver_car_data = pd.merge_asof(
                    driver_car_data, driver_laps_date,
                    left_on='Date', right_on='LapStartDate', direction='backward')
                driver_car_data.drop(columns=['LapStartDate', 'DriverAhead'], inplace=True)
                driver_car_data = driver_car_data.replace({pd.NaT:None, np.nan:None}).copy()
                
                if not driver_car_data.empty:
                    driver_car_data['lap_id'] = driver_car_data['LapNumber'].map(lap_map)
                    driver_car_data['time_'] = driver_car_data['Time'].dt.total_seconds()
                    driver_car_data['Date'] = pd.to_datetime(driver_car_data['Date'])
                    driver_car_data['SessionTime'] = driver_car_data['SessionTime'].dt.total_seconds()

                    car_dicts = driver_car_data[[
                        'lap_id', 'Date', 'time_', 'SessionTime', 'RPM', 'Speed',
                        'nGear', 'Throttle', 'Brake', 'DRS', 'TrackStatus', 'Distance',
                        'DifferentialDistance', 'RelativeDistance', 'DistanceToDriverAhead'
                    ]].rename(columns={
                        'Date': 'date_time', 'SessionTime': 'session_time', 'RPM': 'rpm', 'Speed': 'speed',
                        'nGear': 'n_gear', 'Throttle': 'throttle', 'Brake': 'brake', 'DRS': 'drs',
                        'TrackStatus': 'track_status', 'Distance': 'distance', 'DifferentialDistance': 'differential_distance',
                        'RelativeDistance': 'relative_distance', 'DistanceToDriverAhead': 'distance_driver_ahead'
                    }).to_dict(orient='records')
                    print(car_dicts)
                    db.bulk_insert_mappings(CarData, car_dicts)
                    db.flush()
            except Exception as e:
                print(f"Error loading data for car_data : {e}. Skipping.")
                continue
            try:

                driver_laps = laps.pick_drivers(driver_number).sort_values('LapStartDate')
                driver_laps_date = driver_laps[['LapStartDate', 'LapNumber']].copy()
                driver_laps_date = driver_laps_date[driver_laps_date['LapStartDate'].apply(isinstance,args= [datetime.datetime])]

                driver_pos_data = driver_laps.get_pos_data().add_track_status()
                driver_pos_data['Date'] = pd.to_datetime(driver_pos_data['Date'])
                driver_pos_data['Status'] = driver_pos_data['Status'].apply(lambda s: True if s == "OnTrack" else False)
                driver_pos_data = driver_pos_data.sort_values('Date')
                driver_pos_data = pd.merge_asof(
                    driver_pos_data, driver_laps_date,
                    left_on='Date', right_on='LapStartDate', direction='backward')
                driver_pos_data.drop(columns=['LapStartDate'], inplace=True)
                driver_pos_data = driver_pos_data.replace({pd.NaT:None, np.nan:None}).copy()
            
                if not driver_pos_data.empty:
                    driver_pos_data['lap_id'] = driver_pos_data['LapNumber'].map(lap_map)
                    driver_pos_data['time_'] = driver_pos_data['Time'].dt.total_seconds()
                    driver_pos_data['Date'] = pd.to_datetime(driver_pos_data['Date'])

                    driver_pos_data['SessionTime'] = driver_pos_data['SessionTime'].dt.total_seconds()
                    pos_dicts = driver_pos_data[[
                        'lap_id', 'Date', 'time_', 'SessionTime', 'X', 'Y', 'Z', 'Status', 'TrackStatus'
                    ]].rename(columns={
                        'Date': 'date_time', 'SessionTime': 'session_time', 'X': 'x', 'Y': 'y', 
                        'Z': 'z', 'Status': 'car_status', 'TrackStatus': 'track_status'
                    }).to_dict(orient='records')

                    db.bulk_insert_mappings(PosData, pos_dicts)
                    db.flush()
            except Exception as e:
                print(f"Error loading data for pos_data : {e}. Skipping.")
                continue
        db.commit()
