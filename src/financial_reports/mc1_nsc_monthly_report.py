# This script retrieves MC1NSC records from two maplecourt database tables that contain 
# all business transactions.
from datetime import datetime, timedelta

from math import floor

from src.utils.file_paths import access_app_data

def mc1_nsc_report(pool, nsc_start, filters):
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
    data_insert_query = """
        insert ignore into maplecourt.MC1nsc_expenses (Date, Description, Amount, StatementID)
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
                                    'MC1NSC', -1), 
                                ' TO ', 1), 
                            'FROM', 1),
                        'MC1 NSC', -1)) as Description, 
                        sum(Amount) as Amount,
                        min(ID) as ID
                    from maplecourt.Statement_biz 
                    where Type = 'Debit'
                    and ((lower(Reference) like '%mc1%nsc%')
                    or (lower(Reference) like '%mc1%_sc%'))
                    and Date between %s and %s
                    group by Description, Date
                ),
                cte_priv as (
                    select 
                        date(Date) as Date, 
                        trim(leading ' ' from substring_index(
                            substring_index(
                                substring_index(
                                    substring_index(
                                        upper(Reference), 
                                    'MC1NSC', -1), 
                                ' TO ', 1), 
                            'FROM', 1),
                        'MC1 NSC', -1)) as Description, 
                        sum(Amount) as Amount,
                        min(ID) as ID
                    from maplecourt.Statement_priv 
                    where Type = 'Debit'
                    and ((lower(Reference) like '%mc1%nsc%')
                    or (lower(Reference) like '%mc1%_sc%'))
                    and Date between %s and %s
                    group by Description, Date
                )
            select * from cte_biz
            union
            select * from cte_priv
        ) as combined_statement;
    """
   
    # Query to retrieve relevant non-service charge records for reporting (refactor date to month start)
    get_non_service_charge_data = """select ID, Date, Description, Amount 
    from maplecourt.MC1nsc_expenses where date between %s and %s;"""

    nsc_start =  datetime.strptime(nsc_start, '%Y-%m-%d') if nsc_start is not None else datetime.now().replace(day=1) # Use a start date if specified, else use month start
    nsc_stop = datetime(nsc_start.year + (1 if nsc_start.month == 12 else 0), (nsc_start.month + 1) % 12 if nsc_start.month != 11 else 12, 1) - timedelta(days=1)

    # In order to maintain track of total service charge since app start date a json file to write prev_net (used for bal brought forward) at the end of every month is created.
    # To ensure total service charge is available at any point in time, the script also writes a curr_net that adds the prev_net to the months grand total.
    # I adopted this structure to avoid multiple wrong additions to the prev net each time the script is run within the same data period during testing or manual runs.
    try:        
        app_data = access_app_data('r')
        nsc_net_summary = app_data['bills']['nsc']
        mgt_fee_percent = app_data['rates']['mgt_fee_%']
    except Exception as e:
        print('Unable to load app data\n',e)

    try:
        cursor.execute(data_insert_query, (nsc_start, nsc_stop, nsc_start, nsc_stop))
        cursor.execute(get_non_service_charge_data, (nsc_start, nsc_stop))
        records = cursor.fetchall()

        if records:
            # Filter records based on specific description
            filtered_records = [record for record in records if all(filter not in record[2] for filter in filters)]
            nsc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]
            subtotal_1 = sum(record[3] for record in filtered_records)
            subtotal_2 = 0 # ub-total after applying 10% markup
            columns = cursor.column_names
            serial_num = 0

            print(f'S/N  :  {columns[0]:5}  :  {columns[1]:10} : {columns[2]:45} : {columns[3]} : AMOUNT2')
            print('------------------------------------------------------------------------------------------------------')
            for record in filtered_records:
                # Format date to display date only
                id = record[0]
                formatted_date = record[1].strftime('%Y-%m-%d')
                description = record[2]
                amount = float(record[3])
                amount2 = 100 * floor(amount * 1.1 / 100) if '.' not in description else amount # Applying 10% markup to the nearest 100 on amount
                subtotal_2 += amount2
                amount2 = f"{amount2:,.2f}" # Formating digits to two decimal places.
                nsc_table_data.append([serial_num, id, formatted_date, description, amount2])
                serial_num += 1
                # Print statement for easy analysis of original amounts against marked up amounts.
                print(f'{serial_num:3}  :  {id:10}  :  {formatted_date:10}  :  {description:45}  :  {amount:10}  :  {amount2:8}')
            print('------------------------------------------------------------------------------------------------------')
            print(f"{'Subtotal 1':78}  :  {subtotal_1:-10,.2f}")
            print(f"{'Subtotal 2':78}  :  {subtotal_2:-10,.2f}")

            nsc_subtotal = subtotal_2
            nsc_management_fee = nsc_subtotal * mgt_fee_percent / 100
            nsc_grand_total = subtotal_2 + nsc_management_fee

            print(f"{'Management fee':78}  :  {nsc_management_fee:-10,.2f}")
            print(f"{'Grand total':78}  :  {nsc_grand_total:-10,.2f}")   

            try:
                # Update json file
                nsc_net_summary['bill_total'] = round(nsc_grand_total,2)
                nsc_net_summary['bill_start_date'] = nsc_start.strftime('%Y-%m-%d')
                nsc_net_summary['bill_stop_date'] = nsc_stop.strftime('%Y-%m-%d')
                
                access_app_data('w', app_data)
            except Exception as e:
                print('Unable to update bal brought forward json file\n', e)  
            nsc_summary_dict = {"subtotal":nsc_subtotal, "mgt_fee":nsc_management_fee, "grand_total":nsc_grand_total}                 
            return nsc_table_data, nsc_summary_dict
        else:
            print('No records retrieved.\n')
            nsc_table_data = [['S/N', 'ID', 'DATE', 'DESCRIPTION', 'AMOUNT(N)']]
            nsc_subtotal = 0.0
            nsc_management_fee = 0.0
            nsc_grand_total = 0.0
            nsc_summary_dict = {"subtotal":nsc_subtotal, "mgt_fee":nsc_management_fee, "grand_total":nsc_grand_total}                 
            return nsc_table_data, nsc_summary_dict
        
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")
    