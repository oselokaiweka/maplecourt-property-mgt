from src.utils import pool_connection

from src.financial_reports import *


if __name__ == '__main__':
    pool = pool_connection()
    
    # NON-SERVICE CHARGE FUNCTION
    filters = ['CLEARED']
    start_date = '2023-11-01'
    nsc_table_data, nsc_summary_dict = mc1_nsc_report(pool, start_date, filters)
    
    # MANAGEMENT FEE FUNCTION
    date1 = '2023-11-01'
    date2 = '2023-11-30'
    mgtfee_table_data, mgtfee_summary_dict = mc1_mgt_report(pool, date1, date2)

    # SERVICE CHARGE FUNCTION 
    sc_start = '2023-11-01' # Use month start if None is specified. 
    sc_table_data, sc_summary_dict = mc1_sc_report(pool, sc_start)

    # INFLOW FUNCTION
    inf_start = '2023-11-01'
    inflow_records = get_landlord_inflow(pool, inf_start)

    # BILL SETTLEMENT FUNCTION
    mc1_settle_bill()

    # GENERATE PDF FUNCTION
    generate_pdf(nsc_table_data, nsc_summary_dict, # <<< NSC VARIABLES
                mgtfee_table_data, mgtfee_summary_dict, # <<< MGT FEE VARIABLES
                sc_table_data, sc_summary_dict, # <<< SC VARIABLES
                date1) # <<< START DATE