# This script retrieves MC1SC records from two maplecourt database tables that contain 
# all business transactions.
from datetime import datetime, timedelta

from src.utils.file_paths import access_app_data
from src.utils.credentials import pool_connection

# Query Retrieves records for mc1 service charge expenses from the given start date and loads transformed 
# data into S.Charge expenses table. Bear in mind constraints prevent duplicate records using multiple cols and StatementID.
load_new_service_charge_data = """
    insert ignore into maplecourt.MC1sc_expenses (Date, Description, Amount, StatementID)
    select Date, Description, Amount, ID from ( 
        with 
            cte_biz as (
                select 
                    date(Date) as Date, 
                    trim(leading ' ' from substring_index(
                        substring_index(
                            substring_index(
                                substring_index(
                                    upper(Reference), 
                                'MC1SC', -1), 
                            ' TO ', 1), 
                        'FROM', 1),
                    'MC1 SC', -1)) as Description, 
                    sum(Amount) as Amount,
                    min(ID) as ID
                from maplecourt.Statement_biz
                where Type =  'Debit'
                and ((lower(Reference) like '%mc1sc%')
                or (lower(Reference) like '%mc1%_sc%'))
                and lower(Reference) not like '%mc1%nsc%'
                and date(Date) between %s and %s
                group by Description, date(Date)
            ),
            cte_priv as (
                select 
                    date(Date) as Date, 
                    trim(leading ' ' from substring_index(
                        substring_index(
                            substring_index(
                                substring_index(
                                    upper(Reference), 
                                'MC1SC', -1), 
                            ' TO ', 1), 
                        'FROM', 1),
                    'MC1 SC', -1)) as Description, 
                    sum(Amount) as Amount, 
                    min(ID) as ID
                from maplecourt.Statement_priv
                where Type = 'Debit'
                and ((lower(Reference) like '%mc1sc%')
                or (lower(Reference) like '%mc1%_sc%'))
                and lower(Reference) not like '%mc1%nsc%'
                and date(Date) between %s and %s
                group by Description, date(Date)
            )
        select * from cte_biz
        union
        select * from cte_priv
    ) as combined_statement;
"""


# Query to retrieve relevant service charge records for reporting.
get_service_charge_data = """
select ID, Date, Description, Amount 
from maplecourt.MC1sc_expenses where date between %s and %s;
"""
   

def mc1_sc_report(pool, sc_start):
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

    sc_start =  datetime.strptime(sc_start, '%Y-%m-%d') if sc_start is not None else datetime.now().replace(day=1) # Use a start date if specified, else use month start
    sc_stop = datetime(sc_start.year + (1 if sc_start.month == 12 else 0), (sc_start.month + 1) % 12 if sc_start.month != 11 else 12, 1) - timedelta(days=1) # Calculates month end
    # In order to maintain track of total service charge since app start date a json file to write prev_net (used for bal brought forward) at the end of every month is created.
    # To ensure total service charge is available at any point in time, the script also writes a curr_net that adds the prev_net to the months grand total.
    # I adopted this structure to avoid multiple wrong additions to the prev net each time the script is run within the same data period during testing or manual runs.
    try:
        app_data = access_app_data('r')
        sc_net_summary = app_data['bills']['sc']
        mgt_fee_percent = app_data['rates']['mgt_fee_%']
    except Exception as e:
        print('Unable to load app data\n',e)

    try:
        cursor.execute(load_new_service_charge_data, (sc_start, sc_stop, sc_start, sc_stop))
        cursor.execute(get_service_charge_data, (sc_start, sc_stop))
        records = cursor.fetchall()

        if records:
            serial_num = 0
            columns = cursor.column_names
            subtotal = sum(record[3] for record in records) 
            sc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]

            print(f'S/N  :  {columns[0]:5}  :  {columns[1]:10}  :  {columns[2]:45}  :  {columns[3]}')
            print('-----------------------------------------------------------------------------------------------')
            for record in records:
                # Format date to display date only
                id = 'S0' + str(record[0])
                date = record[1].strftime('%Y-%m-%d')
                description = record[2]
                amount = f'{record[3]:,.2f}'
                sc_table_data.append([serial_num, id, date, description, amount])
                serial_num += 1
                # Print statement for quick analysis.
                print(f"{serial_num:3}  :  {id:5}  :  {date:10}  :  {description:45}  :  {record[3]:-10,.2f}")
            print('-----------------------------------------------------------------------------------------------')
            print(f"{'Subtotal':78}  :  {subtotal:-10,.2f}")
            
            subtotal = float(subtotal)
            management_fee = subtotal * mgt_fee_percent / 100
            grand_total = subtotal + management_fee

            print(f"{'Management fee':78}  :  {management_fee:-10,.2f}")
            print(f"{'Grand total':78}  :  {grand_total:-10,.2f}")
            
            try:
                # Update json file
                sc_net_summary['bill_total'] = round(grand_total,2)
                sc_net_summary['bill_start_date'] = sc_start.strftime('%Y-%m-%d')
                sc_net_summary['bill_stop_date'] = sc_stop.strftime('%Y-%m-%d')

                access_app_data('w', app_data)
            except Exception as e:
                print('Unable to update app data file\n',e)
            
            sc_summary_dict = {"subtotal":subtotal, "mgt_fee":management_fee, "grand_total": grand_total}
            return sc_table_data, sc_summary_dict
        else:
            print('No records retrieved.\n')
            sc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]
            subtotal = 0.0
            management_fee = 0.0
            grand_total = 0.0
            sc_summary_dict = {"subtotal":subtotal, "mgt_fee":management_fee, "grand_total": grand_total}
            return sc_table_data, sc_summary_dict
        
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")

if __name__ == '__main__':
    pool = pool_connection()
    start_date = '2023-11-01'
    mc1_sc_report(pool, start_date)