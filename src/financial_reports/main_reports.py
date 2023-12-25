from src.utils.credentials import pool_connection
from src.utils.my_logging import mc_logger
from src.financial_reports import *

logger = mc_logger(log_name='main_report_log', log_level='INFO', log_file='main_report.log')

if __name__ == '__main__':
    logger.info("Processing mc_1 financial report.")
    pool = pool_connection()
    
    # NON-SERVICE CHARGE FUNCTION
    filters = ['CLEARED']
    start_date = '2023-11-01'
    logger.info("Processing non-service charge report.")
    nsc_table_data, nsc_summary_dict = mc1_nsc_report(pool, start_date, filters)
    
    # MANAGEMENT FEE FUNCTION
    date1 = '2023-11-01'
    date2 = '2023-11-30'
    logger.info("Processing management fee report.")
    mgtfee_table_data, mgtfee_summary_dict = mc1_mgt_report(pool, date1, date2)

    # SERVICE CHARGE FUNCTION 
    sc_start = '2023-11-01' # Use month start if None is specified. 
    logger.info("Processing service charge report.")
    sc_table_data, sc_summary_dict = mc1_sc_report(pool, sc_start)

    # INFLOW FUNCTION
    inf_start = '2023-11-01'
    logger.info("Processing inflow reports.")
    inflow_records = get_landlord_inflow(pool, inf_start)

    # BILL SETTLEMENT FUNCTION
    logger.info("Processing bill settlement.")
    mc1_settle_bill()

    # GENERATE PDF FUNCTION
    logger.info("Generating report pdf document.")
    generate_pdf(nsc_table_data, nsc_summary_dict, # <<< NSC VARIABLES
                mgtfee_table_data, mgtfee_summary_dict, # <<< MGT FEE VARIABLES
                sc_table_data, sc_summary_dict, # <<< SC VARIABLES
                date1) # <<< START DATE