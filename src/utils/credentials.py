import os
import psutil
import subprocess
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mysql.connector.pooling import MySQLConnectionPool as mysqlconpool

from src.utils import db_pass, sudopass, dir_path


def get_google_credentials(logger_instance):
    """
    Summary:
        Obtains credentials then initializes the service object used
        for connecting to google api in order to read and send emails.
    Args:
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.
    Returns:
        service (type: object): usage service = build('gmail', 'v1',cre)
    """
    creds = None
    scopes = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    if os.path.exists(dir_path + "/token.json"):
        with open(dir_path + "/token.json", "r") as token:
            creds = Credentials.from_authorized_user_info(json.load(token), scopes)

    if not creds or not creds.valid:
        logger_instance.warning("Failed to obtain valid creddentials")

        if creds and creds.expired and creds.refresh_token:
            logger_instance.info("Trying to refresh credentials...")
            try:
                creds.refresh(Request())
                logger_instance.info("Credentials refreshed successfully.\n")
                with open(dir_path + "/token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger_instance.error("Failed to refresh credentials:", e)

        else:
            logger_instance.info("Attempting to authorise application...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    dir_path + "/client_secret.json", scopes
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(dir_path + "/token.json", "w") as token:
                    token.write(creds.to_json())
                logger_instance.info("Application authorized successfully.")
            except Exception as e:
                logger_instance.error("Failed to authorize application:", e)

    else:
        logger_instance.info("Valid credentials obtained.\n")

    service = build('gmail', 'v1', credentials=creds)
    return service


def start_mysql_service(sudopass, logger_instance):
    """
    Summary:
        Checks if mysqld service is among running processes using psutil and
        starts process using valid user credentials if not found.
    Args:
        sudopass : password (environment variable).
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.
    """
    # Checking if mysql process is running already.
    # The process_iter() method yields a psutil.process object for each process enabling iteration.
    for process in psutil.process_iter():
        if process.name() == "mysqld":
            logger_instance.info(f"MySQL process is already running.")
            return

    # If the MySQL process is not running then start the service.
    logger_instance.info("Starting MySQL service...")
    command = f"echo '{sudopass}' | sudo -S service mysql start"
    subprocess.run(command, shell=True)


def pool_connection(logger_instance):
    """
    Summary:
        Start mysql service and provides pool connection token with valid credentials.
    Args:
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.
    Returns:
        pool: mysql connection pool object.
    """
    start_mysql_service(sudopass, logger_instance)

    db_config = {
        "host": "localhost",
        "user": "admin",
        "password": db_pass,
        "database": "maplecourt",
        "autocommit": True,
        "pool_reset_session": True,
    }
    pool = mysqlconpool(pool_name="mc_pool", pool_size=30, **db_config)
    logger_instance.info(f"MySQL connection pool created.")
    return pool


def get_cursor(pool, logger_instance):
    """
    Summary:
        returns mysql connection and cursor objects
    Args:
        pool (object/variable): mysql connection pool object
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.
    Returns:
        connection, cursor(objects): mysql pool connection and cursor objects
    """    
    try:
        connection = pool.get_connection()
        logger_instance.info(f"Connected to {pool.pool_name} pool successfully\n")
    except:
        pool.add_connection()
        logger_instance.warning(f"Added a new connection to {pool.pool_name} pool\n")
        connection = pool.get_connection()
        logger_instance.info(f"Connected to {pool.pool_name} pool successfully")
    cursor = connection.cursor()
    return connection, cursor

