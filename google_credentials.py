import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



def get_credentials():
    creds  = None
    dir_path = os.environ.get('DIR_PATH')
    scopes = ["https://www.googleapis.com/auth/gmail.send","https://www.googleapis.com/auth/gmail.readonly"] 

    if os.path.exists(dir_path+'/token.json'):
        with open(dir_path+'/token.json', 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), scopes)

    if not creds or not creds.valid:
        print("Failed to obtain valid creddentials")
        
        if creds and creds.expired and creds.refresh_token:
            print("Trying to refresh credentials...")
            try:
                creds.refresh(Request())
                print("Credentials refreshed successfully.\n")
                with open(dir_path+"/token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print("Failed to refresh credentials:", e)

        else:
            print("Attempting to authorise application...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(dir_path+"/client_secret.json", scopes)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(dir_path+"/token.json", "w") as token:
                    token.write(creds.to_json())
                print("Application authorized successfully.")
            except Exception as e:
                print("Failed to authorize application:", e)
                
    else:
        print("Valid credentials obtained.\n")    
    return creds

CREDS = get_credentials()