from datetime import datetime, timedelta, timezone
import fastf1

year = datetime.today().year
RoundNumber = fastf1.get_events_remaining()['RoundNumber'].values[0]
EventFormat = fastf1.get_events_remaining()['EventFormat'].values[0]

if EventFormat == 'conventional':
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session1DateUtc'].values[0])):
        import practice_1
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session2DateUtc'].values[0])):
        import practice_2 
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session3DateUtc'].values[0])):
        import practice_3
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session4DateUtc'].values[0])):
        import quali
    if ((datetime.today() - timedelta(hours=4,minutes=30)) == (fastf1.get_events_remaining()['Session5DateUtc'].values[0])):
        import race

if EventFormat == 'sprint_qualifying':
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session1DateUtc'].values[0])):
        import practice_1
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session2DateUtc'].values[0])):
        import sprint 
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session3DateUtc'].values[0])):
        import sprint_quali
    if ((datetime.today() - timedelta(hours=3,minutes=30)) == (fastf1.get_events_remaining()['Session4DateUtc'].values[0])):
        import quali
    if ((datetime.today() - timedelta(hours=4,minutes=30)) == (fastf1.get_events_remaining()['Session5DateUtc'].values[0])):
        import race