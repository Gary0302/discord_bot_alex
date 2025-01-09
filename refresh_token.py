from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv, set_key, find_dotenv
import json
import logging
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.readonly']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def refresh_google_api_credentials():
    creds = None
    logger.info("Attempting to refresh/create Google API credentials.")

    client_config = json.loads(os.getenv("client_secret"))
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    try:
        creds = flow.run_local_server(port=0)
        if creds:
            set_key(find_dotenv(), "GOOGLE_CREDENTIALS", creds.to_json())
            logger.info("Google API credentials created successfully and saved to environment.")
            return True
        else:
            logger.error("Failed to create new credentials.")
            return False
    except Exception as e:
        logger.error(f"An error occurred during credential creation: {e}")
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                os.environ['GOOGLE_CREDENTIALS'] = creds.to_json()
                logger.info("Google API credentials refreshed successfully and saved to environment.")
                return True
            except Exception as refresh_error:
               logger.error(f"Failed to refresh credentials: {refresh_error}")
               logger.error(f"Attempting to create new credentials again due to refresh failure: {refresh_error}")
               try:
                  creds = flow.run_local_server(port=0)
                  if creds:
                      os.environ['GOOGLE_CREDENTIALS'] = creds.to_json()
                      logger.info("Google API credentials created successfully (after refresh fail) and saved to environment.")
                      return True
                  else:
                      logger.error("Failed to create new credentials after refresh failure.")
                      return False
               except Exception as create_again_error:
                   logger.error(f"Failed to create new credentials (after refresh fail): {create_again_error}")
                   return False
        else:
            logger.error(f"Failed during the initial credential process: {e}")
            return False


if __name__ == "__main__":
    refresh_google_api_credentials()