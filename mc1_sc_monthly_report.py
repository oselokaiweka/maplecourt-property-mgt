# This script retrieves MC1SC records from two maplecourt database tables that contain 
# all business transactions.
from datetime import datetime
from mysql_pool import POOL


# (Refactor date to month start)
# Query Retrieves records for mc1 service charge expenses from the given start date and loads transformed 
# data into S.Charge expenses table. Bear in mind constraints prevent duplicate records using multiple cols and StatementID.
load_new_service_charge_data = """
insert ignore into maplecourt.MC1sc_expenses 
(Date, Description, Amount, StatementID)
select Date, Description, Amount, ID from (
with 
cte_biz as (select
date(sb.Date) as Date, 
trim(leading ' ' from
    substring_index(
        substring_index(
            substring_index(
                substring_index(
                    upper(sb.Reference), 
                'MC1SC', -1), 
            ' TO ', 1), 
        'FROM', 1),
    'MC1 SC', -1)
) as Description, 
sum(sb.Amount) as Amount,
min(sb.ID) as ID
from maplecourt.Statement_biz as sb
where sb.Type =  'Debit'
and lower(sb.Reference) like '%mc1sc%'
and lower(sb.Reference) like '%mc1%_sc%'
and lower(sb.Reference) not like '%mc1%nsc%'
and lower(sb.Reference) not like '%f6%'
and date(sb.Date) between %s and current_date()
group by Description, date(sb.Date)
),
cte_priv as (select
date(sp.Date) as Date, 
trim(leading ' ' from 
    substring_index(
        substring_index(
            substring_index(
                substring_index(
                    upper(sp.Reference), 
                'MC1SC', -1), 
            ' TO ', 1), 
        'FROM', 1),
    'MC1 SC', -1)
) as Description, 
sum(sp.Amount) as Amount, 
min(ID) as ID
from maplecourt.Statement_priv as sp
where sp.Type =  'Debit'
and lower(sp.Reference) like '%mc1sc%'
and lower(sp.Reference) like '%mc1%_sc%'
and lower(sp.Reference) not like '%mc1%nsc%'
and lower(sp.Reference) not like '%f6%'
and date(sp.Date) between %s and current_date()
group by Description, date(sp.Date)
)
select * from cte_biz
union
select * from cte_priv
) as combined_statement;
"""


# Query to retrieve relevant service charge records for reporting (refactor date to month start)
get_service_charge_data = """
select ID, Date, Description, Amount 
from maplecourt.MC1sc_expenses where date >= %s;
"""
   

def mc1_sc_report(pool, monthstart):
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

    try:
        cursor.execute(load_new_service_charge_data, (monthstart, monthstart))
        cursor.execute(get_service_charge_data, (monthstart,))
        records = cursor.fetchall()

        if records:
            print(f'Total number of records: {len(records)}\n')
            
            curr_month_records = [record for record in records if record[1] >= datetime.strptime('2023-09-12','%Y-%m-%d').date() and record[1] <= datetime.strptime('2023-09-30','%Y-%m-%d').date()]
            subtotal = sum(record[3] for record in curr_month_records) 

            serial_num = 1
            columns = cursor.column_names
            # create variable to hold table data as list of lits with the first being the header
            sc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]

            print(f'S/N  :  {columns[0]:5}  :  {columns[1]:10} : {columns[2]:25} : {columns[3]}')
            print('-----------------------------------------------------------------------------')

            for record in curr_month_records:
                # Format date to display date only
                id = 'S0' + str(record[0])
                date = record[1].strftime('%Y-%m-%d')
                description = record[2]
                amount = f'{record[3]:,.2f}'
                sc_table_data.append([serial_num, id, date, description, amount])
                serial_num += 1

                # Print statement for quick analysis.
                print(f'{serial_num:3}  :  {id:10}  :  {date:25} : {description:10}  : {amount:8}')
            print('---------------------------------------------------------------------------')
            print(f'Subtotal                                         :             :   {subtotal}')
            
            subtotal = float(subtotal)
            management_fee = subtotal * 0.075
            grand_total = subtotal + management_fee
            print(grand_total)
            
            sc_summary_list = [subtotal, management_fee, grand_total]


            oct_month_records = [record for record in records if record[1] >= datetime.strptime('2023-10-01','%Y-%m-%d').date() and record[1] <= datetime.strptime('2023-10-31','%Y-%m-%d').date()]
            oct_subtotal = sum(record[3] for record in oct_month_records) 

            oct_serial_num = 1
            columns = cursor.column_names
            # create variable to hold table data as list of lits with the first being the header
            oct_sc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]

            print(f'S/N  :  {columns[0]:5}  :  {columns[1]:10} : {columns[2]:25} : {columns[3]}')
            print('-----------------------------------------------------------------------------')

            for record in oct_month_records:
                # Format date to display date only
                id = 'S0' + str(record[0])
                date = record[1].strftime('%Y-%m-%d')
                description = record[2]
                amount = f'{record[3]:,.2f}'
                oct_sc_table_data.append([oct_serial_num, id, date, description, amount])
                oct_serial_num += 1

                # Print statement for quick analysis.
                print(f'{serial_num:3}  :  {id:10}  :  {date:25} : {description:10}  : {amount:8}')
            print('---------------------------------------------------------------------------')
            print(f'Subtotal                                         :             :   {oct_subtotal}')
            
            oct_subtotal = float(oct_subtotal)
            management_fee = oct_subtotal * 0.075
            grand_total = oct_subtotal + management_fee
            print(grand_total)
            
            oct_sc_summary_list = [oct_subtotal, management_fee, grand_total]


            # Calculating all_sum amount from start point
            all_subtotal = sum(record[3] for record in records) 
            all_mgt_fee = float(all_subtotal) * 0.075
            all_total = float(all_subtotal) + all_mgt_fee
            
            print(all_total)

            return sc_table_data, sc_summary_list, all_total, oct_sc_table_data, oct_sc_summary_list
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
    monthstart = '2023-09-12'
    mc1_sc_report(pool, monthstart)