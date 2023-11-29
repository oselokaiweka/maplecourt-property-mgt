# This script retrieves MC1SC records from two maplecourt database tables that contain 
# all business transactions.
from datetime import datetime, timedelta
from mysql_pool import POOL
import json
import os

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
   

def mc1_sc_report(pool, sc_start1):
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

    sc_start =  sc_start1 if sc_start1 is not None else datetime.now().replace(day=1) # Use a start date if specified, else use month start
    # In order to maintain track of total service charge since app start date a json file to write prev_net (used for bal brought forward) at the end of every month is created.
    # To ensure total service charge is available at any point in time, the script also writes a curr_net that adds the prev_net to the months grand total.
    # I adopted this structure to avoid multiple wrong additions to the prev net each time the script is run within the same data period during testing or manual runs.
    try:
        dir_path = os.environ.get('DIR_PATH')
        with open(dir_path+"/mc_app_config.json", "r") as net_file: # Get balance brought forward saved in json file
            net_summary = json.load(net_file)
        sc_net_summary = net_summary['sc']
        prev_net = sc_net_summary['prev_net']
    except Exception as e:
        print('Unable to retrieve balance brought forward')
        prev_net = 0.0

    try:
        cursor.execute(load_new_service_charge_data, (sc_start, sc_start))
        cursor.execute(get_service_charge_data, (sc_start,))
        records = cursor.fetchall()

        if records:
            serial_num = 1
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
            management_fee = subtotal * 0.075
            grand_total = subtotal + management_fee
            curr_net = prev_net + grand_total

            print(f"{'Management fee':78}  :  {management_fee:-10,.2f}")
            print(f"{'Grand total':78}  :  {grand_total:-10,.2f}")
            print(f"{'Net balance':78}  :  {curr_net:-10,.2f}")
            
            try:
                # Update json file
                sc_net_summary['curr_net'] = curr_net
                sc_net_summary['curr_date'] = datetime.now().strftime('%Y-%m-%d')
                # Set previous net to current net if date is >= end of the following month since the last prev net was set.
                prev_date = datetime.strptime(sc_net_summary['prev_date'], '%Y-%m-%d')
                next_month_end = datetime(prev_date.year, prev_date.month + 2, 1) - timedelta(days=1)
                sc_net_summary['prev_net'] = curr_net if datetime.now() >= next_month_end else prev_net
                sc_net_summary['prev_date'] = datetime.now().strftime('%Y-%m-%d') if datetime.now() >= next_month_end else prev_date.strftime('%Y-%m-%d')
                with open(dir_path+"/mc_app_config.json", "w") as net_file:
                    json.dump(net_summary, net_file, indent=4) # Use indent for pretty formatting
            except Exception as e:
                print('Unable to update bal brought forward json file\n', e)
            
            sc_summary_dict = {"subtotal":subtotal, "mgt_fee":management_fee, "grand_total": grand_total, "curr_net": curr_net}
            return sc_table_data, sc_summary_dict
        else:
            print('No records retrieved.\n')
            sc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]
            subtotal = 0.0
            management_fee = 0.0
            grand_total = 0.0
            curr_net = prev_net
            sc_summary_dict = {"subtotal":subtotal, "mgt_fee":management_fee, "grand_total": grand_total, "curr_net": curr_net}
            return sc_table_data, sc_summary_dict
        
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")

if __name__ == '__main__':
    pool = POOL
    sc_start = '2023-10-01'
    mc1_sc_report(pool, sc_start)