# This script essentially extracts transaction records from csv file that is downloaded
# monthly then filters and wrangles the data and finally loads the transformed data 
# into mysql database table for business analysis, reconciliation and reporting.


# Importing necessary libraries: 
import re
import sys
import codecs
import logging
import locale
import subprocess
import pandas as pd 
from mysql_pool import POOL # Starts MySQL service and obtains connection pool object
from datetime import datetime
import mysql.connector as connector

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, #Level set to DEBUG for more detailed logs but can be set to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/oseloka/chrometro-expenses-data/private_statement_etl_logger.log',
    filemode='w'
)
# Create logger
logger = logging.getLogger('csv_file_priv_logger')
# Create a fileHandler with immediate flushing
file_handler = logging.FileHandler('csv_file_priv.log', mode='w')
file_handler.flush = True
logger.addHandler(file_handler)

# Defining the file path for stdout and stderr redirection
stdout_file = "/home/oseloka/chrometro-expenses-data/private_statement_etl_stdout.txt"
stderr_file = "/home/oseloka/chrometro-expenses-data/private_statement_etl_stderr.txt"

# Open the files in write mode to redirect the output
with open(stdout_file, 'w') as sys.stdout, open(stderr_file, 'w') as sys.stderr:
    logging.info("std redirection is setup")
    
    # Encoding source file to utf-8
    def data_encoding(input_file, output_file):
        input_encoding = 'us-ascii'
        output_encoding = 'utf-8'
        try:
            with open(input_file, 'r', encoding=input_encoding, errors='ignore') as source_file:
                logging.info('Input file definition successful')
                with open(output_file, 'w', encoding=output_encoding) as target_file:
                    logging.info('output file definition successful')
                    for line in source_file:
                        try:
                            target_file.write(line)
                            logging.info('target file write successful')
                        except Exception as e:
                            logging.error(f'target file write error:\n{e}')
        except Exception as e:
            logging.error(f'encoding error:\n{e}')
    
    # DATA EXTRAXTION AND TRANSFORMATION
    def data_transformation(file):
        logging.info('Applying transformation to data')
        try:
            # Put needed column numbers into needed_columns variable:
            needed_columns = [0, 3, 4, 5, 6]
            logging.info('put columns')
            not_number = ["", "-","- "," -"]
            logging.info('put neggative handler')
            
            # Import desired records into pandas data frame:
            df = pd.read_csv(file, usecols=needed_columns, header=None, skiprows=1, na_values=not_number, encoding='utf-8')
            logging.info('Required columns successfully captured')
            
            try:
                # Changing the date format for column 0:
                df[0] = pd.to_datetime(df[0], format='%d-%b-%y').dt.strftime('%Y-%m-%d')
                logging.info('Date formatting successful')
            except Exception as e:
                logging.info(f'date formatting error\n{e}')

            # Converting columns 3, 4, 5 to sql decimal type:
            df[3] = df[3].apply(lambda x: locale.atof(x.replace(',', '')) if isinstance(x, str) else x) # Removing comma from digits
            df[3] = pd.to_numeric(df[3], errors='coerce')
            df[4] = df[4].apply(lambda x: locale.atof(x.replace(',', '')) if isinstance(x, str) else x)
            df[4] = pd.to_numeric(df[4], errors='coerce')
            df[5] = df[5].apply(lambda x: locale.atof(x.replace(',', '')) if isinstance(x, str) else x)
            df[5] = pd.to_numeric(df[5], errors='coerce')
            logging.info('decimal conversion successful')

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
            logging.info('Reference formatting successful')

            logging.info('Data transformation completed successfully')
            for row in df.itertuples(index=False, name=None):
                print(row)
            return df
        
        except Exception as e:
            logging.error(f'Data transformation failed,\n{e.args[1]}\n')
            logging.error(e)
            sys.exit() # Exit the entire process if data extraction or transformation fails. 


    # DATA LOADING
    def data_loading(pool, df, file1, file2):
        # Obtain pool connection or adds connection if pool is exhausted 
        try:
            connection = pool.get_connection()
            logging.info(f"connected to {pool.pool_name} pool successfully.\n" )
        except:
            pool.add_connection()
            logging.info(f"Added a new connection to the {pool.pool_name} pool.")
            connection = pool.get_connection()
            logging.info(f"connected to {pool.pool_name} pool successfully.\n")
        cursor = connection.cursor()

        try:
            # Starts MySQL event scheduler so that any triggers affected by operation will be executed.
            logging.info('Starting DB event scheduler...')
            cursor.execute("SET GLOBAL event_scheduler =  ON;")
            logging.info('Event scheduler is started.\n')

            # Loading data into the database table
            logging.info('Inserting records into table...')
            if not df.empty:
                # Prepare the INSERT statement according to order of columns in db:
                insert_query = """INSERT IGNORE INTO Statement_priv 
                    (Date, Type, Amount, Reference, CurrentBal) 
                    VALUES (%s, %s, %s, %s, %s);"""
        
                insert_count = 0
                duplicate_count = 0
                for row in df.itertuples(index=False, name=None): 
                    try:
                        if pd.isnull(row[1]):
                            cursor.execute(insert_query, (row[0], 'Credit', row[2], row[4], row[3]))
                            insert_count += 1
                        elif pd.isnull(row[2]):
                            cursor.execute(insert_query, (row[0], 'Debit', row[1], row[4], row[3]))
                            insert_count +=1
                    except connector.IntegrityError as e:
                        if "Duplicate entry" in str(e):
                            duplicate_count += 1
                            logging.warning(f"Duplicate entry: {row} - {e}")
                        else:
                            logging.error(f"Error inserting record: {row} - {e}")
                    except Exception as e:
                        logging.error(e.args[1]) # args[1] prints only the error message without the error number.

                connection.commit()
                cursor.close()
                connection.close()
                logging.info(f'ETL complete!\nTotal of {insert_count} records where inserted.\nConnection closed\n')
                logging.info(f"Skipped {duplicate_count} rows due to duplicate entries.")
                # Remove statement csv files to make room for next etl
                command = f"rm -fv {file1} {file2}"
                subprocess.run(command, shell=True)
            else:
                logging.info('Insert process terminated - No new record for insert.\n')
        except Exception as e:
            logging.error(e)


    if __name__ == "__main__":
        start_timer = datetime.now()
        logging.info(f'PROCESS START TIME...........................................................................: {start_timer}\n')

        # Execute data extraction and transformation then return value into data insert arguement
        input_file = "/home/oseloka/chrometro-expenses-data/private_statement.csv"
        output_file = "/home/oseloka/chrometro-expenses-data/private_statement_utf-8.csv"

        data_encoding(input_file, output_file)

        df = data_transformation(output_file)

        # Execute data insert
        pool = POOL
        data_loading(pool, df, input_file, output_file)

        logging.info(f'PROCESS DURATION.............................................................................: {(datetime.now()-start_timer).total_seconds()}\n')
    

    