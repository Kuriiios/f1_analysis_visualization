from instagrapi import Client
import os
from pathlib import Path
import fastf1

year = int(input('Year ? '))
race_number = int(input('Race Number ? (1-24) '))
race_session = input('Session ? (Q, SQ, R, S) ')

def session_type(race_session):
    match race_session:
        case 'Q':
            return 'Qualifying'
        case 'SQ':
            return 'Sprint Qualifying'
        case 'R':
            return 'Race'
        case 'S':
            return 'Sprint Race'

session = fastf1.get_session(year, race_number, race_session)
session.load()

caption =  ( f"🇦🇺 Round {session.event.RoundNumber} - {session.event.EventName} ({session.event.Country})\n"
            f"📍 {session.event.Location}\n"
            f"🏁 {session_type(race_session)} Session Recap\n"
            f"———\n"
            f"Stay tuned for full weekend coverage of the {session.event.OfficialEventName}!\n"
            f"#F1 #Formula1 #F1{session.event.RoundNumber} #F1{session.event.Country.replace(' ', '')} #F1Weekend #F1Quali #F1Race #F1Team")

parent_file = Path(__file__).resolve().parent.parent
#print(parent_file)
def read_credentials(file= parent_file / "login.txt"):
    creds = {}
    with open(file) as f:
        for line in f:
            key, value = line.strip().split("=")
            creds[key] = value
    return creds

# Usage
creds = read_credentials()
cl = Client()
cl.login(creds['username'], creds['password'])

# Define image paths (local paths to your images)
if race_session == 'Q' or race_session == 'SQ':
    for i in range(3):
        image_folder = parent_file / f"reports/{session.event.RoundNumber}_{session.event.EventName}_{year}/{session.event.RoundNumber}_Q{str(i+1)}_{session_type(race_session)}"
        image_files = []

        for report in os.listdir(image_folder):
            image_files.append(os.path.join(image_folder, report))
        # Post as a carousel
        cl.album_upload(
            paths=image_files,
            caption=caption
            )
        cl.delay_range = [1, 3]
elif race_session == 'R' or race_session == 'S':
    image_folder = parent_file / f"reports/{session.event.RoundNumber}_{session.event.EventName}_{year}/{session.event.RoundNumber}_{session_type(race_session)}"
    image_files = []

    for report in os.listdir(image_folder):
        image_files.append(os.path.join(image_folder, report))

    # Post as a carousel
    cl.album_upload(
        paths=image_files,
        caption=caption
        )
    cl.delay_range = [1, 3]