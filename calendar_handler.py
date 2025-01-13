from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil.parser import parse

def get_upcoming_events(service, time_window_hours=24):
    now = datetime.utcnow()
    later = now + timedelta(hours=time_window_hours)

    now_iso = now.isoformat() + 'Z'
    later_iso = later.isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_iso,
        timeMax=later_iso,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    # include time zone in the result so date parsing is timezone aware
    return [{"id": event.get('id'),
             "summary": event.get('summary'),
             "start": parse(event['start'].get('dateTime')).isoformat() if event['start'].get('dateTime') else None,
             "end": parse(event['end'].get('dateTime')).isoformat() if event['end'].get('dateTime') else None} for event in events]