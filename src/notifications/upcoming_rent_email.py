#Importing necessary libraries and modules:
import time
import base64
from datetime import datetime, timedelta

from crontab import CronTab
import mysql.connector as connector
from googleapiclient.discovery import build
from email.mime.text import MIMEText #for creating email messages with text content
from email.mime.multipart import MIMEMultipart #for creating email messages with text content

from src.utils.file_paths import sys_user
from src.utils.credentials import pool_connection
from src.utils.credentials import get_google_credentials


def send_upcoming_rent_email(pool):

    # Variables to schedule cron job
    plus_hour = (datetime.now())+(timedelta(hours=1)) # Current time plus one hour.
    USER =  sys_user
    my_cron = CronTab(user=USER)

    # Query statement to fetch records of upcominng rentals that are 1 or 2 or 3 months away.
    upcoming_rent_records = """SELECT concat(T.FirstName,' ',T.LastName) as TenantName, 
    T.Email, U.RentPrice, U.ServiceCharge, R.StopDate, (U.RentPrice + U.ServiceCharge) as Total
    FROM Units U inner join Tenants T using (UnitID)
    inner join Rentals R using (TenantID) 
    where R.StopDate = date_add(curdate(), interval 1 month) 
    or R.StopDate = date_add(curdate(), interval 2 month)
    or R.StopDate = date_add(curdate(), interval 3 month)
    or R.StopDate = curdate();"""

    try:
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n" )
    except:
        pool.add_connection()
        print(f"Added a new connection to the {pool.pool_name} pool.")
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n")
    cursor = connection.cursor()

    try:
        print('Checking for upcoming rent...')
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()
        if records:
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
                body = f"Dear {tenant_name},\n\nThis is a friendly reminder that your tenancy expires on {due_date}.\nWe are happy with your tenancy and hereby extend you an offer to renew your tenancy as detailed below:\n\nOUTSTANDING RENT:  NGN{rent_amount}\nSERVICE CHARGE:  NGN{service_charge}\nTOTAL:  NGN{payment_total}\n\nKindly respond to this email stating if you will be renwing or not renewing.\nPlease note that accepting to renew is accepting to make full payment on or before {due_date}.\n\nFailure to respond will be treated as decline to this offer.\n\nThank you for your prompt response.\n\nThank You and Best Regards, \nADMIN - CHROMETRO NIG\nMAPLE COURT APARTMENTS"
                message.attach(MIMEText(body, "Plain"))
                print(f"Creating email for {tenant_name}...\n")

                #Send email message. Reset cron job to 10am everyday in case it has been modifiied by the exception.
                try:
                    CREDS = get_google_credentials
                    service = build('gmail', 'v1', credentials=CREDS)

                    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
                    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
                    print(f"Email sent to {tenant_name} successfully!\n")

                    # Reset cron job to 10am everyday.
                    try:
                        for job in my_cron:
                            if job.comment == 'upcoming_rent_email':
                                job.setall('0 10 * * *')
                                my_cron.write()
                                print(f"The '{job.comment}' cron job has been successfully reset as follows:")
                                print(f"{job}\n")
                    except Exception as e:
                        print("Unable to reset cron job to 10am everyday.")
                    
                except Exception as e:
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
                        print(f"\nUnable to reschedule cron job which means email of today {datetime.date}, if any, was not sent!")
            time.sleep(1) #A 1 second delay between each iteration of loop to avoid excessive resource usage
        else:
            print('No upcoming rent data found.')
    except connector.Error as error:
        print(error)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")
        

if __name__ == "__main__":
    print(f'PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n')
    pool = pool_connection()
    send_upcoming_rent_email(pool) 
