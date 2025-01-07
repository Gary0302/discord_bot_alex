from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_recent_emails(service):
    # 抓取最近的郵件
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])
    email_data = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        email_data.append({"id": msg['id'], "snippet": msg_data['snippet']})

    return email_data