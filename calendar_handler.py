from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def get_upcoming_events(service):
    # 設定時間範圍
    now = datetime.utcnow().isoformat() + 'Z'
    later = (datetime.utcnow() + timedelta(hours=24)).isoformat() + 'Z'

    # 抓取行程
    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=later, singleEvents=True, orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return [{"id": event.get('id'),"summary": event.get('summary'), "start": event['start'].get('dateTime')} for event in events]