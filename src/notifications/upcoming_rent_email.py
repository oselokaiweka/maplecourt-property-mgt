# Importing necessary libraries and modules:
import time
from datetime import datetime, timedelta

import mysql.connector as connector

from src.utils.comms import send_email
from src.utils.file_paths import sys_user
from src.utils.workflow import reschedule_cron_job
from src.utils.credentials import pool_connection, get_google_credentials


def create_email_body(tenant_name, due_date, rent_amount, service_charge, payment_total):
    """
    Function creates email body for upcoming rent to tenants based on
    provided parameters. 

    Args:
        tenant_name (str or varchar): Supplied as variable obtained from database.
        due_date (date): Supplied as variable obtained from database.
        rent_amount (decimal): Supplied as variable obtained from database.
        service_charge (decimal): Supplied as variable obtained from database.
        payment_total (decimal): rent_amount + service_charge.

    Returns:
        Variable: Variable initialized with email body multi-line string. 
    """    
    body = (
        f"Dear {tenant_name},\n\n"
        f"This is a friendly reminder that your tenancy expires on {due_date}.\n"
        "We are happy with your tenancy and hereby extend you an offer to renew your tenancy as detailed below:\n\n"
        f"OUTSTANDING RENT:  NGN{rent_amount}\n"
        f"SERVICE CHARGE:  NGN{service_charge}\n"
        f"TOTAL:  NGN{payment_total}\n\n"
        "Kindly respond to this email stating if you will be renewing or not renewing.\n"
        f"Please note that accepting to renew is accepting to make full payment on or before {due_date}.\n\n"
        "Failure to respond will be treated as a decline to this offer.\n\n"
        "Thank you for your prompt response.\n\n"
        "Thank You and Best Regards,\n"
        "ADMIN - CHROMETRO NIG\n"
        "MAPLE COURT APARTMENTS"
    )
    return body


def send_upcoming_rent_email(pool):
    """
    Checks for rent stopdates in rental database table that are today or 3,2 or 1 month from today and
    sends email notification to the respective tenants from the tenant database table.

    Args:
        pool (object): mysql connection pool object obtained from imported pool_connection function.
    """
    # Variables to schedule cron job
    plus_hour = (datetime.now()) + (timedelta(hours=1))  # Current time plus one hour.
    USER = sys_user

    # Query statement to fetch records of upcominng rentals that are 1 or 2 or 3 months away.
    upcoming_rent_records = """
        SELECT concat(T.FirstName,' ',T.LastName) as TenantName, 
        T.Email, U.RentPrice, U.ServiceCharge, R.StopDate, (U.RentPrice + U.ServiceCharge) as Total
        FROM Units U inner join Tenants T using (UnitID)
        inner join Rentals R using (TenantID) 
        where R.StopDate in (date_add(curdate(), interval 1 month),
                             date_add(curdate(), interval 2 month),
                             date_add(curdate(), interval 3 month),
                             curdate());
    """

    try:
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n")
    except:
        pool.add_connection()
        print(f"Added a new connection to the {pool.pool_name} pool.")
        connection = pool.get_connection()
        print(f"connected to {pool.pool_name} pool successfully.\n")

    cursor = connection.cursor()

    try:
        print("Checking for upcoming rent...")
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()

        if records:
            print("Upcoming rent data found.\n")
            for record in records:
                tenant_name, email, rent_amount, service_charge, due_date, payment_total = record[:5]

                body = create_email_body(tenant_name, due_date, rent_amount, service_charge, payment_total)
                print(f"Creating email for {tenant_name}...\n")

                success = send_email("Upcoming Rent Renewal", "admin@chrometronig.com", email, body, get_google_credentials())

                if success:
                    print(f"Email sent to {tenant_name} successfully!\n")
                    reschedule_cron_job(USER, "upcoming_rent_email", "0 10 * * *")
                else:
                    print(f"Email not sent to {tenant_name}. Modifying cron job to send email in 1 hour...\n")
                    reschedule_cron_job(USER, "upcoming_rent_email", f"{plus_hour.minute} {plus_hour.hour} * * *")
                
                time.sleep(1)
        else:
            print("No upcoming rent found.")
    except connector.Error as error:
        print(error)
    finally:
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")


if __name__ == "__main__":
    print(f"PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n")
    pool = pool_connection()
    send_upcoming_rent_email(pool)
