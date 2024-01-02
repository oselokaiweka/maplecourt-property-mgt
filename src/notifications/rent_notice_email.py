# Importing necessary libraries and modules:
from datetime import datetime, timedelta

import mysql.connector as connector

from src.utils.comms import send_email
from src.utils.my_logging import mc_logger
from src.utils.file_paths import sys_user, read_config
from src.utils.workflow import reschedule_cron_job
from src.utils.credentials import pool_connection, get_cursor, get_google_credentials

logger = mc_logger(log_name='rent_notice_log', log_level='INFO', log_file='rent_notice.log')


def create_email_body(tenant_name, due_date, rent_amount, service_charge, payment_total, landlord, bank, logger_instance):
    """
    Function creates email body for upcoming rent to tenants based on
    provided parameters. 

    Args:
        tenant_name (str or varchar): Supplied as variable obtained from database.
        due_date (date): Supplied as variable obtained from database.
        rent_amount (decimal): Supplied as variable obtained from database.
        service_charge (decimal): Supplied as variable obtained from database.
        payment_total (decimal): rent_amount + service_charge.
        landlord (str): Full name of property landlord.
        bank (str): 'Bank_name - account_number' as one str.
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.

    Returns:
        body: Variable initialized with multi-line email body string. 
    """  
    body = (
        f"Dear {tenant_name},\n\n"
        f"This is a friendly reminder that your tenancy expires on {due_date}.\n"
        "We are happy with your tenancy and hereby extend you a renewal offer as detailed below:\n\n"
        f"OUTSTANDING RENT:  NGN{rent_amount:,.2f}\n"
        f"SERVICE CHARGE:  NGN{service_charge:,.2f}\n"
        f"TOTAL:  NGN{payment_total:,.2f}\n\n"
        "Kindly respond to this email stating if you will be renewing or not renewing.\n"
        f"Please note that accepting to renew is accepting to make full payment on or before {due_date} to the bank detail below:\n\n"
        f"ACCOUNT NAME: {landlord}\n"
        f"ACCOUNT NUMBER: {bank}\n\n"
        "Failure to respond will be treated as a decline to this offer.\n"
        "Your prompt response is greatly appreciated.\n\n"
        "Thank You and Best Regards,\n"
        "ADMIN - CHROMETRO NIG\n"
        "MAPLE COURT APARTMENTS"
    )

    logger_instance.info("Email body created")  
    return body


def send_upcoming_rent_email(logger_instance):
    """
    Checks for rent stopdates in rental database table that are today or 3,2 or 1 month from today and
    sends email notification to the respective tenants from the tenant database table.

    Args:
        logger_instance (object): Inherits logger_instance in script where function is imported into for logging consistency.
    """
    # Variables to schedule cron job
    plus_hour = (datetime.now()) + (timedelta(hours=1))  # Current time plus one hour.
    USER = sys_user

    # Query statement to fetch records of upcominng rentals that are 1 or 2 or 3 months away.
    upcoming_rent_records = """
    SELECT 
        CONCAT(T.FirstName, ' ', T.LastName) AS TenantName,
        T.Email,
        U.RentPrice,
        U.ServiceCharge,
        R.StopDate,
        (U.RentPrice + U.ServiceCharge) AS Total,
        L.FullName AS Landlord,
        L.BankDetails AS Bank
    FROM
        Rentals R
            INNER JOIN
        Tenants T ON R.TenantID = T.TenantID
            INNER JOIN
        Units U ON T.UnitID = U.UnitID
            INNER JOIN
        Property P ON U.PropertyID = P.ID
            INNER JOIN
        Landlords L ON P.LandlordID = L.LandlordID
    WHERE
        R.StopDate IN (
            DATE_ADD(CURDATE(), INTERVAL 1 MONTH),
            DATE_ADD(CURDATE(), INTERVAL 2 MONTH),
            DATE_ADD(CURDATE(), INTERVAL 3 MONTH),
            DATE_ADD(CURDATE(), INTERVAL 59 DAY)
        )
    ;
    """

    try:
        pool = pool_connection(logger_instance)
        connection, cursor = get_cursor(pool, logger_instance)

        config = read_config(logger_instance)
        app_email = config.get('Email', 'app_email_address')

        logger_instance.info("Checking for upcoming rent...")
        cursor.execute(upcoming_rent_records)
        records = cursor.fetchall()

        if records:
            logger_instance.info("Upcoming rent data found.\n")
            for record in records:
                logger_instance.info(f"{record} / {len(cursor.description)}")
                tenant_name, email, rent_amount, service_charge, due_date, payment_total, landlord, bank = record[:8]

                body = create_email_body(tenant_name, due_date, rent_amount, service_charge, payment_total, landlord, bank, logger_instance)
                logger_instance.info(f"Creating email for {tenant_name}...\n")
                success = send_email("Upcoming Rent Renewal", app_email, email, body, logger_instance)

                if success:
                    logger_instance.info(f"Email sent to {tenant_name} successfully!\n")
                    reschedule_cron_job(USER, "rent_notice_email", "0 10 * * *", logger_instance)
                else:
                    logger_instance.warning(f"Email not sent to {tenant_name}. Modifying cron job to send email in 1 hour...\n")
                    reschedule_cron_job(USER, "rent_notice_email", f"{plus_hour.minute} {plus_hour.hour} * * *", logger_instance)

        else:
            logger_instance.info("No upcoming rent found.")

    except connector.Error as error:
        logger_instance.error(f"Unable to retrieve rental details from database:\n{error}")

    except Exception as e:
        logger_instance.exception(f"An error occured", exc_info=True)

    finally:
        cursor.close()
        connection.close()
        logger_instance.info("Connection and cursor closed.\n")


if __name__ == "__main__":
    
    logger.info(f"PROCESS RUN TIMESTAMP...........................................................................: {datetime.now()}\n")

    send_upcoming_rent_email(logger)
