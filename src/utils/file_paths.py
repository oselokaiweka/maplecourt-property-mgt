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
    with open(
        dir_path + "/resources/dynamic/mc_app_data.json", mode
    ) as app_data_file:  # Get app data from json file
        if mode == "r":
            app_data = json.load(app_data_file)
            return app_data
        elif mode == "w":
            app_data = args[0]
            json.dump(app_data, app_data_file, indent=4)  # Use indent for pretty format
        else:
            print("Error, Mode accepts 'r' and 'w' only")
