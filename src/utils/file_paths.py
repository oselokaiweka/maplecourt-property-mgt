import os
import json

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
