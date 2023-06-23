#!/bin/sh

# Start of log entry
echo
echo
echo "........................................................START OF BACKUP PROCESS_$(date +%d-%m-%Y_%H-%M-%S)"
echo
# Importing environment variable (db login credentials) from .bash_profile
. /home/oseloka/.bash_profile
PASSWORD=$DB_PASS
USERPASS=$SUDO_PASS

# Initializing local variables
BACKUP_DIRECTORY=/home/oseloka/db_backups

DATABASE=maplecourt

DUMPFILE_SQL=$BACKUP_DIRECTORY/$DATABASE-$(date +%d-%m-%Y_%H-%M-%S).sql

DUMPFILE_GZ=$BACKUP_DIRECTORY/$DATABASE-$(date +%d-%m-%Y_%H-%M-%S).gz

# Backup retention period
PERIOD=1


# Check if mysql process is running if not then start process
if ! pgrep mysql >/dev/null; then
	echo "MySQL process is stopped. Starting process..."
	echo $USERPASS | sudo -S service mysql start
	echo "MySQL process is now running"


else
	echo "MySQl process is already running"
fi


# Download sql dump file
if mysqldump -u admin -p$PASSWORD $DATABASE > $DUMPFILE_SQL; then
	echo "$DATABASE dump file successfully downloaded for archiving"

	# Compress downloaded file
        if gzip -c $DUMPFILE_SQL > $DUMPFILE_GZ; then
        	echo "$DATABASE backup successfully compressed and archived"
        	echo $USERPASS | sudo -S rm $DUMPFILE_SQL

		# Delete old backups longer than 30 days
		echo $USERPASS | sudo -S find $BACKUP_DIRECTORY -mtime +$PERIOD -delete



    	else
        	echo "Error creating $DATABASE backup file, process terminated"
        	echo $USERPASSrm | sudo -S rm $DUMPFILE_SQL
    	fi



else
	echo "Encountered and error, $DATABASE backup process failed"
fi

echo
echo "........................................................END OF BACKUP PROCESS_$(date +%d-%m-%Y_%H-%M-%S)"
echo
