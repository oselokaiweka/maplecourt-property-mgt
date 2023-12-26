from datetime import datetime
from src.utils.credentials import pool_connection
from src.utils.my_logging import mc_logger
from src.financial_reports import *

logger = mc_logger(log_name='main_report_log', log_level='INFO', log_file='main_report.log')

if __name__ == '__main__':
    logger.info(f"PROCESSING MC1 FINANCIAL REPORT..... {datetime.now()}\n")

    try:
        logger.info("Obtaining MySQL connection pool to access maplecourt database.")
        pool = pool_connection(logger)
    except Exception as e:
        logger.exception(f"Main error obtaining pool connection")


    try:
        # MANAGEMENT FEE FUNCTION
        date1 = '2023-12-01'
        date2 = '2023-12-31'
        logger.info("Processing management fee report.")
        mgtfee_table_data, mgtfee_summary_dict = mc1_mgt_report(pool, date1, date2, logger)
        logger.info("Processing management fee report completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing mgt report")


    try:
        # SERVICE CHARGE FUNCTION 
        sc_start = date1 # Use month start if None is specified. 
        logger.info("Processing service charge report.")
        sc_table_data, sc_summary_dict = mc1_sc_report(pool, sc_start, logger)
        logger.info("Processing service charge report completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing sc report")


    try:   
        # NON-SERVICE CHARGE FUNCTION
        filters = ['CLEARED']
        start_date = date1
        logger.info("\nProcessing non-service charge report.")
        nsc_table_data, nsc_summary_dict = mc1_nsc_report(pool, start_date, filters, logger)
        logger.info("Processing non-service charge report completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing nsc report")


    try:
        # INFLOW FUNCTION
        inf_start = date1
        logger.info("Processing inflow reports.")
        inflow_records = get_landlord_inflow(pool, inf_start, logger)
        logger.info("Processing inflow reports completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing inflow report.\n")


    try: 
        # BILL SETTLEMENT FUNCTION
        logger.info("Processing bill settlement.")
        mc1_settle_bill(logger)
        logger.info("Processing bill settlement completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing bill settlement report")


    try:
        # GENERATE PDF FUNCTION
        logger.info("Generating report pdf document.")
        generate_pdf(nsc_table_data, nsc_summary_dict, # <<< NSC VARIABLES
                    mgtfee_table_data, mgtfee_summary_dict, # <<< MGT FEE VARIABLES
                    sc_table_data, sc_summary_dict, # <<< SC VARIABLES
                    date1, # <<< START DATE
                    logger) # <<< LOGGER
        logger.info("Generating report pdf document completed successfully.\n")
    except Exception as e:
        logger.exception(f"Main error processing generate report pdf")


    logger.info(f"Processing mc_1 financial report completed successfully..... {datetime.now()}\n")