# This script essentially extracts transaction records from csv file that is downloaded
# monthly then filters and wrangles the data and finally loads the transformed data 
# into mysql database table for business analysis, reconciliation and reporting.


# Importing necessary libraries: 
import sys
from datetime import datetime

import re
import locale
import pandas as pd 
import mysql.connector as connector

from src.utils.credentials import pool_connection, get_cursor
from src.utils.file_paths import read_config, data_encoding, delete_file
from src.utils.my_logging import mc_logger

# Setup my_logger
my_logger = mc_logger(log_name='etl_priv', log_level='INFO', log_file='etl_log.log')


# DATA EXTRAXTION AND TRANSFORMATION
def data_transformation(file):
    my_logger.info('Applying transformation to data')
    try:
        # Put needed column numbers into needed_columns variable:
        needed_columns = [0, 3, 4, 5, 6]
        my_logger.info('put columns')
        not_number = ["", "-","- "," -"]
        my_logger.info('put neggative handler')
        
        # Import desired records into pandas data frame:
        df = pd.read_csv(file, usecols=needed_columns, header=None, skiprows=1, na_values=not_number, encoding='utf-8')
        my_logger.info('Required columns successfully captured')
        
        try:
            # Changing the date format for column 0:
            df[0] = pd.to_datetime(df[0], format='%d-%b-%y').dt.strftime('%Y-%m-%d')
            my_logger.info('Date formatting successful')
        except Exception as e:
            my_logger.error(f'date formatting error\n{e}')

        # Converting columns 3, 4, 5 to sql decimal type:
        decimal_columns = [3,4,5]
        df[decimal_columns] = df[decimal_columns].apply(lambda x: locale.atof(x.replace(',', '')) if isinstance(x, str) else x) # Removing comma from digits
        df[decimal_columns] = pd.to_numeric(df[3], errors='coerce')
        my_logger.info('decimal conversion successful')

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
        my_logger.info('Reference formatting successful')
        my_logger.info('Data transformation completed successfully')

        return df
    
    except Exception as e:
        my_logger.error(f'Data transformation failed,\n{e.args[1]}\n')
        sys.exit() # Exit the entire process if data extraction or transformation fails. 


# DATA LOADING
def data_loading(df, file1, file2):
    my_logger.info('Initiating data loading')
    # Obtain pool connection or adds connection if pool is exhausted 
    pool = pool_connection()
    connection, cursor = get_cursor(pool)

    try:
        # Starts MySQL event scheduler so that any triggers affected by operation will be executed.
        my_logger.info('Starting DB event scheduler...')
        cursor.execute("SET GLOBAL event_scheduler =  ON;")
        my_logger.info('Event scheduler is started.\n')

        # Loading data into the database table
        my_logger.info('Inserting records into table...')
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
                        my_logger.warning(f"Duplicate entry: {row} - {e}")
                    else:
                        my_logger.error(f"Error inserting record: {row} - {e}")

                except connector.Error as e:
                    my_logger.error(f"MySQL connector error: {e}")

                except Exception as e:
                    my_logger.error(e.args[1]) # args[1] prints only the error message without the error number.

            connection.commit()
            my_logger.info(f'ETL complete!\nTotal of {insert_count} records where inserted.\nConnection closed\n')
            my_logger.info(f"Skipped {duplicate_count} rows due to duplicate entries.")
            
            # Remove statement csv files to make room for next etl
            files_to_delete = [file1, file2]
            for file in files_to_delete:
                try:
                    delete_file(file)
                    my_logger.info(f"File {file} deleted.")
                except Exception as e:
                    my_logger.error(f"Error deleting file {file}: {e}")
            

        else:
            my_logger.info('Insert process terminated - No new record for insert.\n')
    
    except Exception as e:
        my_logger.error(e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            my_logger.info("Database connection is closed")


if __name__ == "__main__":
    start_timer = datetime.now()
    my_logger.info(f'PROCESS START TIME...........................................................................: {start_timer}\n')

    # Execute data extraction and transformation then return value into data insert arguement
    config = read_config()
    input_file = config.get('FilePaths', 'etl_priv_input_file')
    output_file = config.get('FilePaths', 'etl_priv_output_file')

    try:
        data_encoding(input_file, output_file)
        my_logger.info(f"File encoding completed successfully")
    except Exception as e:
        my_logger.error(f"File encoding failed: {e}")

    df = data_transformation(output_file)
    data_loading(df, input_file, output_file)

    my_logger.info(f'PROCESS DURATION.............................................................................: {(datetime.now()-start_timer).total_seconds()}\n')


