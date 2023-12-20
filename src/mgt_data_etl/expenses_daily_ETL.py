#Importing necessary libraries and modules:
import sys
from decimal import Decimal
from datetime import datetime, timedelta

from src.utils.file_paths import sys_user, access_app_data
from src.utils.workflow import reschedule_cron_job
from src.utils.credentials import pool_connection, get_cursor
from src.utils.comms import read_email

def extract_mc_transaction(sender, start_date, stop_date, subject):
    """
        Retrieves records of transactions pertaining to maple court property management
        from email transaction notifications. 

    Args:
        sender (str): sender title
        start_date (date str): date from which retrieval begins
        stop_date (date str): date from which retrieval ends
        subject (str): email subject

    Returns:
        records (tuple): Comprises of date-time, alert type, amount, reference and current balance. 
    """    
    try:
        email_data = read_email(sender, start_date, stop_date, subject)

        records = []

        for email_entry in email_data:
            subject = email_entry['subject']
            body = email_entry['email_body']

            try:
                amount = Decimal(subject[5][:-1].replace(',',''))
                alert_type = subject[3][1:-1]              
                date_time = datetime.strptime(body[0]+' '+body[1], '%d-%m-%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
                reference = ' '.join(body[body.index('Remarks')+ 1: body.index('Time')])
                current_bal = Decimal(body[body.index('Current')+4].replace(',',''))
            except Exception as e:
                print(f"Error extracting email data with subject: {subject}, error: {e}")

            records.append((date_time , alert_type , amount , reference , current_bal))

        records = sorted(records, reverse = False) #Sorting the record so it inserts from the oldest to the newest.
        print('Records Extracted, Transformed and ready for Loading...\n')
        
        return records
                
    except Exception as e:
        print(e)
        # Reschedule cron job to retry script after 1 hour:
        SYS_USER = sys_user
        job_comment = 'upcoming_rent_email'
        schedule = '{minute} {hour} * * *'.format(minute=plus_hour.minute, hour=plus_hour.hour)
        reschedule_cron_job(SYS_USER, job_comment, schedule)
        sys.exit()


def data_insert(records):
    """
        Inserts records of transactions pertaining to maple court property management
        as retrieved from email transaction notifications by extract_mc_transaction() and 
        loads data into Cashflow table in the mysql aplecourt database.

    Args:
        records (tuple): Extracted email records
    """    
    if records:
        try:
            pool = pool_connection()
            connection, cursor = get_cursor(pool)

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
                # Update start_date value with stop_date value so next time the script runs it will begin from where it stopped in the last run.
                app_data['expenses_daily_etl']['start_date'] = stop_date
                access_app_data('w', app_data)
                print("Next ETL operation has been scheduled for tomorrow.")
            except Exception as e:
                print("Unable to reschedule the start date, however data duplication is resticted in database so only new records will be inserted.\n",e)

        except Exception as e:
            print(e)
            # Reschedule cron job to retry script after 1 hour:
            SYS_USER = sys_user
            job_comment = 'expenses_daily_ETL'
            schedule = '{minute} {hour} * * *'.format(minute=plus_hour.minute, hour=plus_hour.hour)
            reschedule_cron_job(SYS_USER, job_comment, schedule)
            sys.exit()
    else:
        print('Insert process terminated - No new record for insert.\n')
    
    # Reschedule cron job to 11am everyday.
    SYS_USER = sys_user
    job_comment = 'expenses_daily_ETL'
    schedule = '0 11 * * *'
    reschedule_cron_job(SYS_USER, job_comment, schedule)
    

if __name__ == "__main__":
    print(f'PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n')
    
    # Variables to schedule cron job
    plus_hour = (datetime.now())+(timedelta(hours=1)) # Current time plus one hour.

    try:
        # Set stop_date arguement to now.
        stop_date = datetime.now().strftime("%Y/%m/%d")
        print(f'Stop date is set for: {stop_date}\n')

        # Read start date from mc_app_data.json
        app_data = access_app_data('r')
        start_date = app_data['expenses_daily_etl']['start_date']
        print(f'Start date is set for: {start_date}\n')

        # Execute data extraction and transformation.
        records = extract_mc_transaction('GeNS@gtbank.com', start_date, stop_date, 'GeNS Transaction *')

        #  Execute data insert
        data_insert(records)

    except Exception as e:
        print(e)
