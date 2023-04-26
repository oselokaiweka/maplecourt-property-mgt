#Importing necessary libraries and modules:
import base64 #for encoding and decoding data in base64 format
import time
import datetime
import json
import os
import subprocess
import mysql.connector as connector
from mysql.connector.pooling import MySQLConnectionPool as mysqlconpool
from email.mime.text import MIMEText #for creating email messages with text content
from email.mime.multipart import MIMEMultipart #for creating email messages with text content
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from crontab import CronTab
import psutil

def start_mysql_service(sudopass):
    # Check if the MySQL process is running
    for process in psutil.process_iter():
        if process.name() == "mysqld":
            print("MySQL process is already running.")
            return
        
    # If the MySQL process is not running then start the service.
    print("Starting MySQL service...")
    command = f"echo '{sudopass}' | sudo -S service mysql start"
    subprocess.run(command, shell=True)
        

SCOPES = ["https://www.googleapis.com/auth/gmail.send"] #scope limits gmail access to 'send' only



def get_credentials():
    creds  = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

    if not creds or not creds.valid:
        print("Failed to obtain valid creddentials")
        
        if creds and creds.expired and creds.refresh_token:
            print("Trying to refresh credentials...")
            try:
                creds.refresh(Request())
                print("Credentials refreshed successfully")
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print("Failed to refresh credentials:", e)

        else:
            print("Attempting to authorise application...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file("/home/oseloka/pyprojects/maplecourt_py/MapleCourt_propertyMgt/client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
                print("Application authorized successfully.")
            except Exception as e:
                print("Failed to authorize application:", e)
                
    else:
        print("Valid credentials obtaineed.")    
    return creds



def send_upcoming_rent_email():
    # Start MySQL service with password
    sudo_password = os.environ.get('SUDO_PASS')
    start_mysql_service(sudo_password)

    # Variables to schedule cron job
    plus_hour = (datetime.datetime.now())+(datetime.timedelta(hours=1)) # Current time plus onee hour.
    my_cron = CronTab(user="oseloka")

    # Variables for DB connection
    db_pass = os.environ.get('DB_PASS')
    db_config = {"host":"localhost", "user":"admin", "password":db_pass, "database":"maplecourt", "autocommit":True}
    pool = mysqlconpool(pool_name="mc_pool", pool_size=30, **db_config)

    # Query statement to fetch records of upcominng rentals that are 1 or 2 or 3 months away.
    upcoming_rent_records = """SELECT concat(T.FirstName,' ',T.LastName) as TenantName, 
    T.Email, R.RentPrice, R.ServiceCharge, R.StopDate, (R.RentPrice + R.ServiceCharge) as Total
    FROM Tenants T inner
    join Rentals R using (UnitID) 
    where StopDate = date_add(curdate(), interval 1 month) 
    or StopDate = date_add(curdate(), interval 2 month)
    or StopDate = date_add(curdate(), interval 3 month);"""

    try:
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully" )
    except:
        pool.add_connection()
        print(f"Added a new connection to the {pool.pool_name} pool ")
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully" )
    try:
        cursor = connection.cursor()
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()
        for record in records:
            tenant_name = record[0]
            email = record[1]
            rent_amount = record[2]
            service_charge = record[3]
            due_date = record[4]
            payment_total = record[5]

            #creating email message
            message = MIMEMultipart()
            message["Subject"] = "Upcoming Rent Renewal"
            message["From"] = "admin@chrometronig.com"
            message["To"] = email
            body = f"Dear {tenant_name},\n\nThis is a friendly reminder that your rent expires on {due_date}.\nWe are happy with your tenancy and hereby extend you an offer to renew your tenancy as detailed below:\n\nRENT:  NGN{rent_amount}\nSERVICE CHARGE:  NGN{service_charge}\nTOTAL:  NGN{payment_total}\n\nKindly respond to this email stating if you will be renwing or not renewing.\nPlease note that accepting to renew is accepting to make full payment on or before {due_date}.\n\nFailure to respond will be treated as decline to this offer.\n\nThank you for your prompt response.\n\nThank You and Best Regards, \nADMIN - CHROMETRO NIG\nMAPLE COURT APARTMENTS"
            message.attach(MIMEText(body, "Plain"))
            print(f"Creating email for {tenant_name}")

            #Send email message and reset cron job to 9am everyday in case it has been moodifiied by the exception.
            try:
                creds = get_credentials()
                service = build('gmail', 'v1', credentials=creds)

                create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
                send_message = (service.users().messages().send(userId="me", body=create_message).execute())
                print(f"Email sent to {tenant_name} successfully!")

                # Reset cron job to 9am everyday.
                try:
                    for job in my_cron:
                        if job.comment == 'upcoming_rent_email':
                            print(job)
                            job.setall('0 9 * * *')
                            my_cron.write()
                            print(f"The '{job.comment}' cron job has been successfully reset as follows:")
                            print(job)

                except Exception as e:
                    print("Unable to reset cron job to 9am everyday.")
                
            except Exception as e:
                subprocess.run(['echo', f'email to {tenant_name} failed to send, crontab will attempt to resend email in 1 hour. Check output file for more details'])
                print(f"Exception: {str(e)}. cron job is being modified to send email in 1 hour...")
                try:
                    # Modify cron job to cron job to retry script after 1 hour:
                    for job in my_cron:
                        if job.comment == 'upcoming_rent_email':
                            job.setall('{minute} {hour} * * *'.format(minute=plus_hour.minute, hour=plus_hour.hour))
                            my_cron.write()
                            print(f"The '{job.comment}' cron job has been successfully modified as follows:")
                            print(job)

                except Exception as e:
                    print(f"<<<<<<<<<<Unable to reschedule cron job which means email of today {datetime.date}, if any, was not sent!>>>>>>>>>>")
                    subprocess.run(['echo', f"<<<<<<<<<<Unable to reschedule cron job which means email of today {datetime.date}, if any, was not sent!>>>>>>>>>>"])
    
                
            time.sleep(1) #A 1 second delay between each iteration of loop to avoid excessive resource usage
    except connector.Error as error:
        print(error)
    

    finally:
        #Return connection back to the pool.add_connection
        connection.close()
        print("Connection returned to pool")



if __name__ == "__main__":  
    send_upcoming_rent_email() 