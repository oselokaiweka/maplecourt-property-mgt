
import os
import psutil
import subprocess
from mysql.connector.pooling import MySQLConnectionPool as mysqlconpool


def start_mysql_service(sudopass):
    # Checking if mysql process is running already. 
    # The process_iter() method yields a psutil.process object for each process enabling iteration.
    for process in psutil.process_iter():
        if process.name() == "mysqld":
            print("MySQL process is already running.")
            return
        
    # If the MySQL process is not running then start the service.
    print("Starting MySQL service...")
    command = f"echo '{sudopass}' | sudo -S service mysql start"
    subprocess.run(command, shell=True)


def pool_connection():
    sudopass = os.environ.get('SUDO_PASS')
    db_pass = os.environ.get('DB_PASS')
    start_mysql_service(sudopass)
    db_config = {
        "host":"localhost", 
        "user":"admin", 
        "password":db_pass, 
        "database":"maplecourt", 
        "autocommit":True, 
        "pool_reset_session": True
    }
    pool = mysqlconpool(pool_name="mc_pool", pool_size=30, **db_config)
    return pool

POOL = pool_connection()