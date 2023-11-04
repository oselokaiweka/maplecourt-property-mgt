# This script retrieves MC1NSC records from two maplecourt database tables that contain 
# all business transactions.
from math import ceil, floor
from mysql_pool import POOL
from datetime import datetime
from mc_inflow import get_landlord_inflow
from mc1_mgt_fee_report import mc1_mgt_report
from mc1_generate_report_pdf import generate_pdf
from mc1_sc_monthly_report import mc1_sc_report

def mc1_nsc_report(pool, date1, filters):
    # Obtain pool connection if available or add connection then obtain pool connection.
    try:
        connection = pool.get_connection()
        print(f'Connected to {pool.pool_name} pool successfully\n')
    except:
        pool.add_connection()
        print(f'Added a new connection to {pool.pool_name} pool\n')
        connection = pool.get_connection()
        print(f'Connected to {pool.pool_name} pool successfully')
    cursor = connection.cursor()

    # Start MySQL event scheduler so any trigger affected by this operation will execute. 
    print('Starting MySQL event scheduler\n')
    cursor.execute("SET GLOBAL event_scheduler = ON;")
    print('Event scheduler is started')

    # Query statement that retrieves records for mc1 expenses for the given start 
    # and end date from two db tables.
    data_insert_query = """insert ignore into maplecourt.MC1nsc_expenses 
    (Date, Description, Amount, StatementID)
    select Date, Description, Amount, ID from (
    with 
    cte_biz as (select 
    date(Date) as Date, 
    trim(leading ' ' from
        substring_index(
            substring_index(
                substring_index(
                    substring_index(
                        upper(Reference), 
                    'MC1NSC', -1), 
                ' TO ', 1), 
            'FROM', 1),
        'MC1 NSC', -1)
    ) as Description, 
    sum(Amount) as Amount,
    min(ID) as ID
    from maplecourt.Statement_biz 
    where Type =  'Debit'
    and lower(Reference) like '%mc1%nsc%'
    and lower(Reference) not like '%f6%'
    and Date between %s and current_date()
    group by Description, Date
    ),
    cte_priv as (select 
    date(Date) as Date, 
    trim(leading ' ' from 
        substring_index(
            substring_index(
                substring_index(
                    substring_index(
                        upper(Reference), 
                    'MC1NSC', -1), 
                ' TO ', 1), 
            'FROM', 1),
        'MC1 NSC', -1)
    ) as Description, 
    sum(Amount) as Amount,
    min(ID) as ID
    from maplecourt.Statement_priv 
    where Type =  'Debit'
    and lower(Reference) like '%mc1%nsc%'
    and lower(Reference) not like '%f6%'
    and Date between %s and current_date()
    group by Description, Date
    )
    select * from cte_biz
    union
    select * from cte_priv
    ) as combined_statement;
    """
   
    # Query to retrieve relevant non-service charge records for reporting (refactor date to month start)
    get_non_service_charge_data = """select ID, Date, Description, Amount 
    from maplecourt.MC1nsc_expenses where date >= %s;"""

    try:
        cursor.execute(data_insert_query, (date1, date1))
        print('pass 1')
        cursor.execute(get_non_service_charge_data, (date1,))
        records = cursor.fetchall()
        if records:
            # Filter records based on specific description
            filtered_records = [record for record in records if record[2] not in filters]
            print(f'Total number of records: {len(records)}')
            print(f'Total number of filtered records: {len(filtered_records)}\n')

            # Expenses sub-total befor applying 10% increase for easy comparison
            subtotal_1 = sum(record[3] for record in filtered_records)
            #Variable to hold sub-total after applying 10% markup
            subtotal_2 = 0 
            serial_num = 1

            columns = cursor.column_names
            # create variable to hold table data as list of lits with the first being the header
            nsc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]

            print(f'S/N  :  {columns[0]:5}  :  {columns[1]:10} : {columns[2]:25} : {columns[3]} : AMOUNT2')
            print('-----------------------------------------------------------------------------')

            for record in filtered_records:
                # Format date to display date only
                id = record[0]
                formatted_date = record[1].strftime('%Y-%m-%d')
                description = record[2]
                amount = record[3]
                amount2 = 100 * floor(float(amount) * 1.1 / 100) # Applying 10% markup to the nearest 100 on amount
                subtotal_2 += amount2
                amount2 = f"{amount2:,.2f}" # Formating digits to two decimal places.
                nsc_table_data.append([serial_num, id, formatted_date, description, amount2])
                serial_num += 1

                # Print statement for easy analysis of original amounts against marked up amounts.
                print(f'{serial_num:3}  : {id:10} : {formatted_date:10}  :  {description:25} : {amount:10}  : {amount2:8}')
            print('---------------------------------------------------------------------------')
            print(f'Subtotal 1                                       :  {subtotal_1}  :')
            print(f'Subtotal 2                                       :             :   {subtotal_2}')
            nsc_management_fee = subtotal_2 * 0.075
            nsc_grand_total = subtotal_2 + nsc_management_fee
            nsc_subtotal = f'{subtotal_2:,.2f}'
            nsc_management_fee = f'{nsc_management_fee:,.2f}'
            nsc_grand_total = f'{nsc_grand_total:,.2f}'
            return nsc_table_data, nsc_subtotal, nsc_management_fee, nsc_grand_total
        else:
            print('No records retrieved.\n')
        
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")

if __name__ == '__main__':
    pool = POOL
    
    # NON-SERVICE CHARGE FUNCTION
    filters = ['ROOF MAINT', 'ROOF MAINTENANCE', 'POP LIGHTING ', 'POP LIGHTING MAT ', 'FENCE WIRE BAL', 'CUT MASQ TREE', 'KITCHEN POLISH BAL', 'CUT TREE GT', 'CUT TREE BAL GT']
    date1 = '2023-09-03'
    nsc_table_data, nsc_subtotal, nsc_management_fee, nsc_grand_total = mc1_nsc_report(pool, date1, filters )
    
    # MANAGEMENT FEE FUNCTION
    date1 = '2023-09-01'
    date2 = '2023-10-31'
    mgtfee_table_data, total_mgt_fee, first_day_prev_month_str = mc1_mgt_report(pool, date1, date2)

    # SERVICE CHARGE PARAMETER
    monthstart = '2023-09-12'

    # SERVICE CHARGE FUNCTION
    sc_table_data, sc_summary_list, all_total, oct_sc_table_data, oct_sc_summary_list = mc1_sc_report(pool, monthstart)

    # INFLOW FUNCTION
    inf_monthstart = datetime.now().replace(day=1)
    inflow_records = get_landlord_inflow(pool, inf_monthstart)

    # GENERATE PDF FUNCTION
    generate_pdf(nsc_table_data, nsc_subtotal, nsc_management_fee, nsc_grand_total, # <<< NSC VARIABLES
                mgtfee_table_data, total_mgt_fee, first_day_prev_month_str, # <<< MGT FEE VARIABLES
                sc_table_data, sc_summary_list, all_total, oct_sc_table_data, oct_sc_summary_list, # <<< SC VARIABLES
                inflow_records) # <<< INFLOW VARIABLES