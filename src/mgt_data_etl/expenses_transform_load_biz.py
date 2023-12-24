# This script essentially extracts transaction records from csv file that is downloaded
# monthly then filters and wrangles the data and finally loads the transformed data 
# into mysql database table for business analysis, reconciliation and reporting.


# Importing necessary libraries: 
import sys
import subprocess
from datetime import datetime

import re
import pandas as pd 
import mysql.connector as connector

from src.utils.credentials import pool_connection, get_cursor
from src.utils.file_paths import read_config, delete_file
from src.utils.my_logging import mc_logger

logger = mc_logger(log_name='etl_biz_log', log_level='INFO', log_file='etl_biz.log')

# DATA EXTRAXTION AND TRANSFORMATION
def data_transformation(file):
    logger.info('Applying transformation to data')
    try:
        # Put needed column numbers into needed_columns variable:
        needed_columns = [0, 3, 4, 5, 6]

        # Import desired records into pandas data frame:
        df = pd.read_csv(file, usecols=needed_columns, header=None, skiprows=1)
        logger.info('Required columns successfully captured')

        # Changing the date format for column 0:
        df[0] = pd.to_datetime(df[0], format='%d-%b-%Y').dt.strftime('%Y-%m-%d')
        logger.info('Date formatting successful')

        # Converting columns 3, 4, 5 to sql decimal type:
        decimal_columns = [3,4,5]
        for column in decimal_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        logger.info('decimal conversion successful')

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
        logger.info('Reference formatting successful')

        logger.info('Data transformation completed successfully')
        return df
    
    except Exception as e:
        logger.error(f"Data transformation failed,\n{e}", exc_info=True)
        sys.exit() # Exit the entire process if data extraction or transformation fails. 


# DATA LOADING
def data_loading(df, file):
    logger.info('Initiating data loading')

    try:
        # Obtain pool connection or adds connection if pool is exhausted 
        pool = pool_connection(logger)
        connection, cursor = get_cursor(pool, logger)

        # Starts MySQL event scheduler so that any triggers affected by operation will be executed.
        cursor.execute("SET GLOBAL event_scheduler =  ON;")
        logger.info('Event scheduler is started.\n')

        # Loading data into the database table
        logger.info('Inserting records into table...')

        if not df.empty:
            insert_query = """INSERT IGNORE INTO Statement_biz 
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
                        logger.warning(f"Duplicate entry: {row} - {e}")
                    else:
                        logger.error(f"Error inserting record: {row} - {e}")

                except connector.Error as e:
                    logger.error(f"MySQL connector error: {e}")

                except Exception as e:
                    logger.error(e.args[1]) # args[1] prints only the error message without the error number.

            connection.commit()
            logger.info(f"ETL complete!\nInserted {insert_count} records.\nSkipped {duplicate_count} duplicate entries.")
        
        else:
            logger.info('Insert process terminated - No new record for insert.\n')
   
    except Exception as e:
        logger.error(f"Error inserting records: {e}", exc_info=True)

    finally: 
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection and cursor are closed")


if __name__ == "__main__":
    start_timer = datetime.now()
    logger.info(f'PROCESS START TIME...........................................................................: {start_timer}\n')

    # Execute data extraction and transformation then return value into data insert arguement
    config = read_config(logger)
    input_file = config.get('FilePaths', 'etl_biz_input_file')

    df = data_transformation(input_file)

    # Execute data insert
    data_loading(df, input_file)

    logger.info(f'PROCESS DURATION.............................................................................: {(datetime.now()-start_timer).total_seconds()}\n')


    