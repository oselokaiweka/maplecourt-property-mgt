#Importing necessary libraries and modules:
import base64 #for encoding and decoding data in base64 format
import time
from datetime import datetime, timedelta
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
from googleapiclient.errors import HttpError
from crontab import CronTab
import psutil
import decimal
from bs4 import BeautifulSoup



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



def obtain_pool_connection(db_pass):
    db_config = {"host":"localhost", "user":"admin", "password":db_pass, "database":"maplecourt", "autocommit":True}
    pool = mysqlconpool(pool_name="mc_pool", pool_size=30, **db_config)  
    try:
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n" )
    except:
        pool.add_connection()
        print(f"Added a new connection to the {pool.pool_name} pool.")
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n")
    return connection 
 


def get_credentials():
    creds  = None
    SCOPES = scopes
    dir_path = str(DIR_PATH)
    if os.path.exists(dir_path+'/token.json'):
        with open(dir_path+'/token.json', 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

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
                flow = InstalledAppFlow.from_client_secrets_file(dir_path+"/client_secret.json", SCOPES)
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


 
def send_upcoming_rent_email():
    
    # Variables to schedule cron job
    plus_hour = (datetime.now())+(timedelta(hours=1)) # Current time plus one hour.
    my_cron = CronTab(user="oseloka")

    # Query statement to fetch records of upcominng rentals that are 1 or 2 or 3 months away.
    upcoming_rent_records = """SELECT concat(T.FirstName,' ',T.LastName) as TenantName, 
    T.Email, R.RentPrice, R.ServiceCharge, R.StopDate, (R.RentPrice + R.ServiceCharge) as Total
    FROM Tenants T inner
    join Rentals R using (UnitID) 
    where StopDate = date_add(curdate(), interval 1 month) 
    or StopDate = date_add(curdate(), interval 2 month)
    or StopDate = date_add(curdate(), interval 3 month);"""

    try:
        connection = CONNECTION 
        cursor = connection.cursor()
        print('Checking for upcoming rent...')
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()
        if records == True:
            print('Upcoming rent data found.\n')
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
                print(f"Creating email for {tenant_name}...\n")

                #Send email message and reset cron job to 9am everyday in case it has been modifiied by the exception.
                try:
                    creds = get_credentials()
                    service = build('gmail', 'v1', credentials=creds)

                    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
                    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
                    print(f"Email sent to {tenant_name} successfully!\n")

                    # Reset cron job to 9am everyday.
                    try:
                        for job in my_cron:
                            if job.comment == 'upcoming_rent_email':
                                print(job)
                                job.setall('0 10 * * *')
                                my_cron.write()
                                print(f"The '{job.comment}' cron job has been successfully reset as follows:")
                                print(f"{job}\n")
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
        else:
            print('No upcoming rent data found.')
    except connector.Error as error:
        print(error)
    finally:
        #Close cursor
        cursor.close()
        print("Cursor is closed.\n")
        


def read_mc_transaction(sender, start_date, stop_date, subject):
    try:
        print('Obtaining credential to read transaction data...')
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        print('Checking for property management expenses data...')

        query = f"from:{sender} after:{start_date} before:{stop_date} subject:{subject}"
        result = service.users().messages().list(userId='me',q=query).execute()
        messages = result.get('messages')

        records = [] #List to coontain entire insert values as a list of tuplles for insert. 

        # Iterate through mail between the speecified date range to obtain email subject and body. 
        if messages:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg['payload']
                headers = payload['headers']
                for header in headers:
                    name = header['name']
                    value = header['value']        
                    if name == 'Subject':
                        subject = value
                subject_list = subject.split()  # Subject_list is email subject converted to list in order to retrieve amountt and alert type.

                if 'parts' in payload:
                    for part in payload['parts']:
                        if 'data' in part['body']:
                            data = part['body']['data']
                            break
                else:
                    if 'data' in payload['body']:
                        data = payload['body']['data']
                    else:
                        continue # skip this message if it doesn't have base64-encoded data
            
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                soup = BeautifulSoup(body,'html.parser')
                email_body = soup.get_text(separator=' ').strip()
                email_body = email_body.split()
                # You can print email_body to see structure of string in order to understand how the following variables are retrieved. 
                
                amount = (subject_list[5][:-1]).replace(',','')
                amount = decimal.Decimal(amount)

                alert_type = (subject_list[3][1:-1])
                
                date_time = (email_body[0]+' '+email_body[1])
                date_time = datetime.strptime(date_time, '%d-%m-%Y %H:%M')
                date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')

                reference = ' '.join(email_body[email_body.index('Remarks')+ 1: email_body.index('Time')])

                current_bal = (email_body[email_body.index('Current')+4]).replace(',','')
                current_bal = decimal.Decimal(current_bal)

                available_bal = (email_body[email_body.index('Available')+4]).replace(',','')
                available_bal = decimal.Decimal(available_bal)

                record = (date_time , alert_type , amount , reference , current_bal , available_bal)
                records.append(record)

            records = sorted(records, reverse = False) #Sorting the record so it inserts from the oldest to the newest.
            print('Data Extracted, Transformed and ready for Loading...\n')
            return records        
        else:
            print('No new transaction data present.')
            return       
    except HttpError as e:
        print(f'encountered an error, {e}\n')
        return



def data_insert(records):
    if records:
        try:
            connection = CONNECTION
            cursor = connection.cursor()
            print('Cursor created.')
            insert_querry = """insert into Cashflow 
            (Date, Type, Amount, Reference, CurrentBal, AvailableBal) 
            values (%s, %s, %s, 
            replace(
                replace(
                    replace(
                        regexp_replace(
                            replace(
                                replace(
                                    regexp_replace(upper(%s), '[0-9]{9,}', ' ' )
                                , 'REF ', ' ')
                            , 'REF: ', ' ')
                        , 'REF:[^\s]+', ' ')
                    , '|', ' ')
                , 'VIA GTWORLD', ' ')
            , 'VIA GAPSLITE', ' '),
            %s, %s)"""
            
            for record in records:
                cursor.execute(insert_querry, record)
            connection.commit()
            connection.close()
            print('ETL complete!\nRecords where successfully inserted ;)\n')
            
        except connector.Error as error:
            print("Data insert operation failed, ", error)
            print()
            return

        try:
            dir_path = DIR_PATH
            # Update start_date value with stop_date value so next time the script runs it will begin from where it stopped in the last run.
            with open(dir_path+"/start_date.txt", "w") as start_date_file:
                    start_date_file.write(stop_date)
            print("Next ETL operation has been scheduled for tomorrow.")

        except Exception as e:
            # Unable to reschedule the start date, however data duplication is resticted in database so only new records will be inserted.
            print("Unable to reschedule the start date, however data duplication is resticted in database so only new records will be inserted.")
    else:
        print('Insert process terminated - No new record for insert.\n')
        return    


if __name__ == "__main__":
    DIR_PATH = "/home/oseloka/pyprojects/maplecourt_py/MapleCourt_propertyMgt"

    # Start MySQL service with password
    sudo_password = os.environ.get('SUDO_PASS')
    start_mysql_service(sudo_password)

    scopes = ["https://www.googleapis.com/auth/gmail.send","https://www.googleapis.com/auth/gmail.readonly"] 

    db_password = os.environ.get('DB_PASS')
    CONNECTION = obtain_pool_connection(db_password)

    send_upcoming_rent_email() 

    stop_date = datetime.now().strftime("%Y/%m/%d")
    with open('start_date.txt','r') as f:
        start_date = f.read().strip()

    records = read_mc_transaction('GeNS@gtbank.com', start_date, stop_date, 'GeNS Transaction *')

    data_insert(records)