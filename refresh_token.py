from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv
load_dotenv()
client_secret = os.getenv("client_secret")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.readonly']

def refresh_google_api_credentials():
    creds = None
    if os.path.exists('credentials.json'):
      creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)

    if not creds or not creds.valid:
         print("Credentials not found or invalid, attempting to create new credentials.")
         flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_109139845358-u3iahd99pa263s47pfoo27l2mttda17b.apps.googleusercontent.com.json', SCOPES)
         creds = flow.run_local_server(port=0)
         if creds:
             with open('credentials.json', 'w') as token:
                 token.write(creds.to_json())
             print("Google API credentials created successfully!")
             return True
         else:
             print("Failed to create new credentials.")
             return False
    elif creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open('credentials.json', 'w') as token:
                token.write(creds.to_json())
            print("Google API credentials refreshed successfully!")
            return True  # 表示憑證已刷新
        except Exception as e:
            print(f"Failed to refresh credentials: {e}")
            print("Attempting to create new credentials.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_109139845358-u3iahd99pa263s47pfoo27l2mttda17b.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
            if creds:
              with open('credentials.json', 'w') as token:
                  token.write(creds.to_json())
              print("Google API credentials created successfully!")
              return True
            else:
              print("Failed to create new credentials.")
              return False
    else:
       print("Credentials are valid and not expired.")
       return True

if __name__ == "__main__":
    refresh_google_api_credentials()