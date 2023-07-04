#Importing necessary libraries and modules:
import os
import sys
import base64
import decimal
from mysql_pool import POOL
from crontab import CronTab
from bs4 import BeautifulSoup
from google_credentials import CREDS
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def read_mc_transaction(sender, start_date, stop_date, subject):
    try:
        print('Obtaining credential to read transaction data...\n')
        service = build('gmail', 'v1', credentials=CREDS)
        print('Checking for property management expenses data...\n')

        query = f"from:{sender} after:{start_date} before:{stop_date} subject:{subject}"
        result = service.users().messages().list(userId='me',q=query).execute()
        messages = result.get('messages')

        records = [] #List to coontain entire insert values as a list of tuples for insert. 

        # Iterate through mail between the specified date range to obtain email subject and body. 
        if messages:
            print('Extracting detected records')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg['payload']
                headers = payload['headers']
                for header in headers:
                    name = header['name']
                    value = header['value']        
                    if name == 'Subject':
                        subject = value
                
                # Subject_list is email subject converted to list in order to retrieve amount and alert type.
                subject_list = subject.split()  

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

                amount = (subject_list[5][:-1]).replace(',','')
                amount = decimal.Decimal(amount)

                alert_type = (subject_list[3][1:-1])
                
                date_time = (email_body[0]+' '+email_body[1])
                date_time = datetime.strptime(date_time, '%d-%m-%Y %H:%M')
                date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')

                reference = ' '.join(email_body[email_body.index('Remarks')+ 1: email_body.index('Time')])

                current_bal = (email_body[email_body.index('Current')+4]).replace(',','')
                current_bal = decimal.Decimal(current_bal)

                record = (date_time , alert_type , amount , reference , current_bal)
                records.append(record)

            records = sorted(records, reverse = False) #Sorting the record so it inserts from the oldest to the newest.
            print('Records Extracted, Transformed and ready for Loading...\n')
            return records        
        else:
            print('No new transaction data present.')
            sys.exit()       
    except HttpError as e:
        print(f'Encountered an error, {e}\n')
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
        sys.exit()


def data_insert(records, pool):
    if records:
        try:
            try:
                connection = pool.get_connection()
                print(f"connected to {pool.pool_name} pool successfully.\n" )
            except:
                pool.add_connection()
                print(f"Added a new connection to the {pool.pool_name} pool.")
                connection = pool.get_connection()
                print(f"connected to {pool.pool_name} pool successfully.\n")
            cursor = connection.cursor()

            print('Starting DB event scheduler...')
            cursor.execute("SET GLOBAL event_scheduler =  ON;")
            print('Event scheduler is started and cursor is closed.\n')

            insert_query = """insert into Cashflow 
            (Date, Type, Amount, Reference, CurrentBal) 
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
            %s)"""
            insert_count = 0
            for record in records:
                try:
                    cursor.execute(insert_query, record)
                    insert_count += 1
                except Exception as e:
                    print(e.args[1])
            connection.commit()
            cursor.close()
            connection.close()
            print(f'ETL complete!\nTotal of {insert_count} records where successfully inserted ;)\n')

            try:
                dir_path = os.environ.get('DIR_PATH')
                # Update start_date value with stop_date value so next time the script runs it will begin from where it stopped in the last run.
                with open(dir_path+"/start_date.txt", "w") as start_date_file:
                        start_date_file.write(stop_date)
                print("Next ETL operation has been scheduled for tomorrow.")
            except Exception as e:
                # Unable to reschedule the start date, however data duplication is resticted in database so only new records will be inserted.
                print("Unable to reschedule the start date, however data duplication is resticted in database so only new records will be inserted.")

        except Exception as e:
            print(e)
            try:
                # Modify cron job to cron job to retry script after 1 hour:
                for job in my_cron:
                    if job.comment == 'expenses_daily_ETL':
                        job.setall('{minute} {hour} * * *'.format(minute=plus_hour.minute, hour=plus_hour.hour))
                        my_cron.write()
                        print(f"The '{job.comment}' cron job has been successfully modified as follows:")
                        print(job)
            except Exception as e:
                print(f"\nUnable to reschedule cron job which means email of today {datetime.date}, if any, was not sent!")
            print()
            sys.exit()
    else:
        print('Insert process terminated - No new record for insert.\n')
    
    # Reset cron job to 11am everyday.
    try:
        for job in my_cron:
            if job.comment == 'expenses_daily_ETL':
                job.setall('0 11 * * *')
                my_cron.write()
                print(f"The '{job.comment}' cron job has been successfully reset as follows:")
                print(f"{job}\n")
    except Exception as e:
        print("Unable to reset cron job to 10am everyday.")
    

if __name__ == "__main__":
    print(f'PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n')
    
    # Variables to schedule cron job
    plus_hour = (datetime.now())+(timedelta(hours=1)) # Current time plus one hour.
    USER =  os.environ.get('SYS_USER')
    dir_path = os.environ.get('DIR_PATH')
    my_cron = CronTab(user=USER)

    try:
        # Set stop_date arguement = now then read start date from file.
        stop_date = datetime.now().strftime("%Y/%m/%d")
        print(f'Stop date is set for: {stop_date}\n')
        with open(f'{dir_path}/start_date.txt','r') as f:
            start_date = f.read().strip()
        print(f'Start date is set for: {start_date}\n')

        # Execute data extraction and transformation then return value into data insert arguement
        records = read_mc_transaction('GeNS@gtbank.com', start_date, stop_date, 'GeNS Transaction *')

        #  Execute data insert
        pool = POOL
        data_insert(records, pool)

    except Exception as e:
        print(e)
