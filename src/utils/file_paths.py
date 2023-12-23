import os
import json
import configparser

from src.utils.my_logging import mc_logger

sys_user = os.environ.get("SYS_USER")
dir_path = os.environ.get("DIR_PATH")
sudopass = os.environ.get("SUDO_PASS")
db_pass = os.environ.get("DB_PASS")




def access_app_data(mode, *args):
    """
    Function to either load or dump data from or to json file (mc_app_data.json).

    Args:
        'r'/'w' (str): Accepts only either 'r' for json.load or 'w' for json.dump.

    Returns:
        dictionary: app_data dictionary.
    """    
    if mode not in ('r','w'):
        raise ValueError("Error, Mode accepts 'r' and 'w' only")
    
    with open(dir_path + "/resources/dynamic/mc_app_data.json", mode) as app_data_file: 
        if mode == "r":
            return json.load(app_data_file)
        elif mode == "w":
            json.dump(args[0], app_data_file, indent=4) # args[0] means the first in *args. 




def read_config():
    """
        Reads config.ini file to obtain file paths, settings and other configurations therein. 

    Returns:
        config (instance/object): Usage: config.get('file_section_header', 'required_variable_name')
    """    
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_path, 'mc_config.ini'))
    return config




# Encoding from us-ascii to utf-8
def data_encoding(input_file, output_file):
    """
        Converts input_file (csv or other data format) from us-ascii encoding to utf-8 encoding
        then writes the converted data to output_file maintaining the same file format. 

    Args:
        input_file (str): Absolute file path
        output_file (str): Absolute file path
    """    
    input_encoding = 'us-ascii'
    output_encoding = 'utf-8'
    try:
        with open(input_file, 'r', encoding=input_encoding, errors='ignore') as source_file:
            with open(output_file, 'w', encoding=output_encoding) as target_file:
                for line in source_file:
                    try:
                        target_file.write(line)
                    except Exception as e:
                        print(e)      
    except Exception as e:
        print(e)




def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(e)