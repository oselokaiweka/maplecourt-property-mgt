# Importing necessary libraries and modules:
from datetime import datetime, timedelta

import mysql.connector as connector

from src.utils.comms import send_email
from src.utils.my_logging import mc_logger
from src.utils.file_paths import sys_user, read_config
from src.utils.workflow import reschedule_cron_job
from src.utils.credentials import pool_connection, get_cursor, get_google_credentials

logger = mc_logger(log_name='rent_notice_log', log_level='INFO', log_file='rent_notice.log')


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

    logger.info("Email body created")  
    return body


def send_upcoming_rent_email():
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
        where R.StopDate in (
            date_add(curdate(), interval 1 month),
            date_add(curdate(), interval 2 month),
            date_add(curdate(), interval 3 month),
            curdate()
        );
    """

    try:
        pool = pool_connection(logger)
        connection, cursor = get_cursor(pool, logger)

        config = read_config(logger)
        app_email = config.get('Email', 'app_email_address')

        logger.info("Checking for upcoming rent...")
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()

        if records:
            logger.info("Upcoming rent data found.\n")
            for record in records:
                tenant_name, email, rent_amount, service_charge, due_date, payment_total = record[:5]

                body = create_email_body(tenant_name, due_date, rent_amount, service_charge, payment_total)
                
                logger.info(f"Creating email for {tenant_name}...\n")
                success = send_email("Upcoming Rent Renewal", app_email, email, body, get_google_credentials(logger))

                if success:
                    logger.info(f"Email sent to {tenant_name} successfully!\n")
                    reschedule_cron_job(USER, "rent_notice_email", "0 10 * * *", logger)
                else:
                    logger.warning(f"Email not sent to {tenant_name}. Modifying cron job to send email in 1 hour...\n")
                    reschedule_cron_job(USER, "rent_notice_email", f"{plus_hour.minute} {plus_hour.hour} * * *", logger)

        else:
            logger.info("No upcoming rent found.")

    except connector.Error as error:
        logger.error(f"Unable to retrieve rental details from database:\n{error}")

    except Exception as e:
        logger.exception(f"An error occured", exc_info=True)

    finally:
        cursor.close()
        connection.close()
        logger.info("Connection and cursor closed.\n")


if __name__ == "__main__":
    
    logger.info(f"PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n")

    send_upcoming_rent_email()
