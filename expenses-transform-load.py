# This script essentially extracts transaction records from csv file that is downloaded
# monthly then filters and wrangles the data and finally loads the transformed data 
# into mysql database table for business analysis, reconciliation and reporting.


# Importing necessary libraries: 
import re
import sys
import subprocess
import pandas as pd 
from mysql_pool import POOL # Starts MySQL service and obtains connection pool object
from datetime import datetime
import mysql.connector as connector

# Defining the file path for stdout and stderr redirection
stdout_file = "/home/oseloka/chrometro-expenses-data/stdout.txt"
stderr_file = "/home/oseloka/chrometro-expenses-data/stderr.txt"

# Open the files in write mode to redirect the output
with open(stdout_file, 'w') as sys.stdout, open(stderr_file, 'w') as sys.stderr:
    # DATA EXTRAXTION AND TRANSFORMATION
    def data_transformation(file):
        print('Applying transformation to data')
        try:
            # Put needed column numbers into needed_columns variable:
            needed_columns = [0, 3, 4, 5, 6]

            # Import desired records into pandas data frame:
            df = pd.read_csv(file, usecols=needed_columns, header=None, skiprows=1)
            print('Required columns successfully captured')

            # Changing the date format for column 0:
            df[0] = pd.to_datetime(df[0], format='%d-%b-%Y').dt.strftime('%Y-%m-%d')
            print('Date formatting successful')

            # Converting columns 3, 4, 5 to sql decimal type:
            df[3] = pd.to_numeric(df[3], errors='coerce')
            df[4] = pd.to_numeric(df[4], errors='coerce')
            df[5] = pd.to_numeric(df[5], errors='coerce')
            print('decimal conversion successful')

            # Defining a method to transform column 6:
            def transform_str(value):
                value = value.upper()
                value = re.sub('[0-9]{9,}', ' ', value)
                value = value.replace('REF ', ' ')
                value = value.replace('REF: ', ' ')
                value = re.sub('REF:[^\s]+', ' ', value)
                value = value.replace('|', ' ')
                value = value.replace('VIA GTWORLD', ' ')
                value = value.replace('VIA GAPSLITE', ' ')
                value = re.sub('\s+', ' ', value)
                return value

            # Applying transformation method to columns 6 from the df:
            df[6] = df[6].apply(transform_str)
            print('Reference formatting successful')

            print('Data transformation completed successfully')
            return df
        
        except Exception as e:
            print(f'Data transformation failed,\n{e.args[1]}\n')
            sys.exit() # Exit the entire process if data extraction or transformation fails. 


    # DATA LOADING
    def data_loading(pool, df, file):
        # Obtain pool connection or adds connection if pool is exhausted 
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
            # Starts MySQL event scheduler so that any triggers affected by operation will be executed.
            print('Starting DB event scheduler...')
            cursor.execute("SET GLOBAL event_scheduler =  ON;")
            print('Event scheduler is started.\n')

            # Loading data into the database table
            print('Inserting records into table...')
            if not df.empty:
                # Prepare the INSERT statement according to order of columns in db:
                insert_query = """INSERT IGNORE INTO Statement_biz 
                    (Date, Type, Amount, Reference, CurrentBal) 
                    VALUES (%s, %s, %s, %s, %s);"""
        
                insert_count = 0
                for row in df.itertuples(index=False, name=None): 
                    try:
                        if pd.isnull(row[1]):
                            cursor.execute(insert_query, (row[0], 'Credit', row[2], row[4], row[3]))
                            insert_count += 1
                        elif pd.isnull(row[2]):
                            cursor.execute(insert_query, (row[0], 'Debit', row[1], row[4], row[3]))
                            insert_count +=1
                    except Exception as e:
                        print(e.args[1]) # args[1] prints only the error message without the error number.

                connection.commit()
                cursor.close()
                connection.close()
                print(f'ETL complete!\nTotal of {insert_count} records where inserted.\nConnection closed\n')
                
                # Delete original csv file to make room for future operation using same file name
                command = f"rm -fv {file}"
                subprocess.run(command, shell=True)
            else:
                print('Insert process terminated - No new record for insert.\n')
        except Exception as e:
            print(e)


    if __name__ == "__main__":
        start_timer = datetime.now()
        print(f'PROCESS START TIME...........................................................................: {start_timer}\n')

        # Execute data extraction and transformation then return value into data insert arguement
        csv_file = "/home/oseloka/chrometro-expenses-data/CHROMETRO_NIGERIA_LTD.csv"
        df = data_transformation(csv_file)

        # Execute data insert
        pool = POOL
        data_loading(pool, df, csv_file)

        print(f'PROCESS DURATION.............................................................................: {(datetime.now()-start_timer).total_seconds()}\n')
    

    