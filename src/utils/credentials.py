import os
import psutil
import subprocess
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mysql.connector.pooling import MySQLConnectionPool as mysqlconpool

from src.utils import db_pass, sudopass, dir_path


def get_google_credentials():
    creds  = None
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



def start_mysql_service(sudopass):
    # Checking if mysql process is running already. 
    # The process_iter() method yields a psutil.process object for each process enabling iteration.
    for process in psutil.process_iter():
        if process.name() == "mysqld":
            print("MySQL process is already running.")
            return
        
    # If the MySQL process is not running then start the service.
    print("Starting MySQL service...")
    command = f"echo '{sudopass}' | sudo -S service mysql start"
    subprocess.run(command, shell=True)


def pool_connection():

    start_mysql_service(sudopass)
    
    db_config = {
        "host":"localhost", 
        "user":"admin", 
        "password":db_pass, 
        "database":"maplecourt", 
        "autocommit":True, 
        "pool_reset_session": True
    }
    pool = mysqlconpool(
        pool_name="mc_pool", 
        pool_size=30, 
        **db_config
    )
    return pool
