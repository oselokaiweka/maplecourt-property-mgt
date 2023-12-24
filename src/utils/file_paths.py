import os
import json
import logging
import configparser

sys_user = os.environ.get("SYS_USER")
dir_path = os.environ.get("DIR_PATH")
sudopass = os.environ.get("SUDO_PASS")
db_pass = os.environ.get("DB_PASS")




def access_app_data(mode, logger, *args):
    """
    Summary:
        Function to either load or dump data from or to json file (mc_app_data.json).
    Args:
        'r'/'w' (str): Accepts only either 'r' for json.load or 'w' for json.dump.
        logger (object): Inherits logger instance in script where function is imported into for logging consistency.
    Returns:
        json data: app_data dictionary.
    """    
    if mode not in ('r','w'):
        raise ValueError("Error, Mode accepts 'r' and 'w' only")
    
    config = read_config(logger)
    app_data_path = config.get('AppData', 'app_data_path')
    
    with open(app_data_path, mode) as app_data_file: 
        if mode == "r":
            logger.info("Loading app data from JSON file.")
            return json.load(app_data_file)
        elif mode == "w":
            logger.info("Writing app data to JSON file.")
            json.dump(args[0], app_data_file, indent=4) # args[0] means the first in *args. 
            logger.info("App data written to JSON file.")




def read_config(logger_instance=None):
    """
    Summary:
        Reads config.ini file to obtain file paths, settings and other configurations therein. 
    Args:
        logger (object): Inherits logger instance in script where function is imported into for logging consistency.
    Returns:
        config (instance/object): Usage: config.get('file_section_header', 'required_variable_name')
    """    
    if logger_instance is None:
        # If logger is not provided, create a new logger
        logger_instance = logging.getLogger(__name__)

    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(dir_path, 'mc_config.ini'))
        logger_instance.info("Read mc_config.ini successful")
        return config
    except Exception as e:
        logger_instance.error(f"Failed to read mc_config.ini file")
    




# Encoding from us-ascii to utf-8
def data_encoding(input_file, output_file, logger):
    """
    Summary:
        Converts input_file (csv or other data format) from us-ascii encoding to utf-8 encoding
        then writes the converted data to output_file maintaining the same file format. 
    Args:
        input_file (str): Absolute file path
        output_file (str): Absolute file path
        logger (object): Inherits logger instance in script where function is imported into for logging consistency. 
    """    
    input_encoding = 'us-ascii'
    output_encoding = 'utf-8'
    try:
        with open(input_file, 'r', encoding=input_encoding, errors='ignore') as source_file:
            with open(output_file, 'w', encoding=output_encoding) as target_file:
                count = 0
                for line_number, line in enumerate(source_file, start=1):
                    try:
                        target_file.write(line)
                        count += 1
                    except Exception as write_error:
                        logger.error(f"Line {line_number}: Error writing to {output_file}: {write_error}")
                logger.info(f"Successfully encoded and written {count} lines output file.")
    except Exception as read_error:
        logger.error(f"Encounterred an error reading {input_file}: {read_error}") 




def delete_file(file_path, logger):
    """
    Summary:
        Deletes specified file. 
    Args:
        file_path (str): Absolute file path
        logger (object): Inherits logger instance in script where function is imported into for logging consistency.
    """    
    try:
        os.remove(file_path)
        logger.info(f"File {file_path} deleted.")
    except FileNotFoundError as e:
        logger.error(f"File {file_path} not found: {e}")
    except Exception as e:
        logger.error(f" Error deleting file {file_path}: {e}")