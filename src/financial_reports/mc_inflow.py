from datetime import datetime, timedelta

from src.utils.file_paths import access_app_data
from src.utils.credentials import get_cursor
from src.utils.my_logging import mc_logger

logger = mc_logger(log_name='mc_inflow_log', log_leve='INFO', log_file='mc_imflow.log')

# Using insert into select to retrieve relevant records from Statement_biz to load into MC_inflow.
# MC_inflow contains records of landlord payments for SC, NSC and MGT fees. 
# Using union all instead of a statement that will contain like and or operators as the former is more efficient. 
insert_mc_inflow = """
insert ignore into MC_inflow (Date, Description, Amount, StatementID)
select Date, UPPER(Reference), Amount, ID from (
    with cte_landlord_inflow as (

        select Date, Reference, Amount, ID from Statement_biz 
        where UPPER(Type) = 'CREDIT'
        and UPPER(Reference) like '%MC1%L1%'
        
        union all
        
        select Date, Reference, Amount, ID from Statement_biz 
        where UPPER(Type) = 'CREDIT'
        and UPPER(Reference) like '%MC2%L1%'
        
        union all
        
        select Date, Reference, Amount, ID from Statement_biz 
        where UPPER(Type) = 'CREDIT'
        and UPPER(Reference) like '%MC2%L2%'
        
        union all
        
        select Date, Reference, Amount, ID from Statement_biz 
        where UPPER(Type) = 'CREDIT'
        and UPPER(Reference) like '%MC2%L3%'
    )
    select * from cte_landlord_inflow where Date >= %s
) as derived_table;
"""

# Updating landlordID and propertyID columns based on Decription column Reference for where LandlordID is null
# code following the like operator in the previous insert_mc_inflow query. 
update_mc_inflow = """
update MC_inflow 
set 
LandlordID = case
    when Description like '%MC1%L1%' then 1
    when Description like '%MC2%L1%' then 1
    when Description like '%MC2%L2%' then 2
    when Description like '%MC2%L3%' then 3
end,
PropertyID = case
    when Description like '%MC1%L1%' then 1
    when Description like '%MC2%L1%' then 2
    when Description like '%MC2%L2%' then 3
    when Description like '%MC2%L3%' then 4
end,
Type = case
    when Description like '%NSC %' then 'NSC'
    when Description like '%SC %' then 'SC'
    when Description like '%MGT %' then 'MGT'
    when Description like '%MANAGEMENT %' then 'MGT'
    else Type
end,
Description = case
    when Description like '%_MC1%L1%' then concat('MC1L1-', trim(leading ' ' from substring_index(Description, 'MC1L1', -1)))
    when Description like '%_MC2%L1%' then concat('MC2L1-', trim(leading ' ' from substring_index(Description, 'MC2L1', -1)))
    when Description like '%_MC2%L2%' then concat('MC2L2-', trim(leading ' ' from substring_index(Description, 'MC2L2', -1)))
    when Description like '%_MC2%L3%' then concat('MC2L3-', trim(leading ' ' from substring_index(Description, 'MC2L3', -1)))
    else Description
end
where LandlordID is null;
""" 
# I Set 'NSC' to be checked before 'SC' in the Type case so SC does not override NSC.
# Included '_' in "..Description like '%_MC2%L3%'.." so each time update is run, updated records are not modified again since
# there will no longer be characters before the MC...


# Get records from mc_inflow for the current month
get_records_from_mc_inflow = """
select i.ID, l.FullName, i.LandlordID, i.PropertyID, i.Amount as Paid
from Landlords l inner join MC_inflow i 
on l.LandlordID = i.LandlordID
where i.Date between %s and %s;
"""

def get_landlord_inflow(pool, inf_start):
    """
        Function inserts into MC_inflow table with relevant records from Statement_biz table, 
        updates columns of same table according to the reference codes, retrieves relevant records
        and posts to mc_app_data.json for management report processing.

    Args:
        pool (object/variable): mysql connection pool object
        inf_start (date str): start date for the records to retrieved and processed.
    """    
    # Obtain pool connection if available or add connection then obtain pool connection.
    # Includes the connection object so that the connection can be closed after operation.
    connection, cursor = get_cursor(pool, logger)

    # Start MySQL event scheduler so any trigger affected by this operation will execute. 
    cursor.execute("SET GLOBAL event_scheduler = ON;")
    logger.info("Event scheduler is started")

    inf_start =  datetime.strptime(inf_start, '%Y-%m-%d') if inf_start is not None else datetime.now().replace(day=1) # Use a start date if specified, else use month start
    inf_stop = datetime(inf_start.year + (1 if inf_start.month == 12 else 0), (inf_start.month + 1) % 12 if inf_start.month != 11 else 12, 1) - timedelta(days=1)
   
    app_data = access_app_data('r', logger)
    payments_data = app_data['payments']
    available_balance = payments_data['available_balance']
    last_payment_id = payments_data['last_payment_id']
    logger.info(f"Last payment id: {last_payment_id}")
    
    try:
        cursor.execute(insert_mc_inflow, (inf_start,))
        cursor.execute(update_mc_inflow)
        cursor.execute(get_records_from_mc_inflow, (inf_start, inf_stop))
        records = cursor.fetchall()

        if records:
            MC1L1_payments = [record for record in records if record[2] == 1 and record[3] == 1 and int(record[0]) > last_payment_id]
            MC2L1_payments = [record for record in records if record[2] == 1 and record[3] == 2 and int(record[0]) > last_payment_id]
            MC2L2_payments = [record for record in records if record[2] == 2 and record[3] == 2 and int(record[0]) > last_payment_id]
            MC2L3_payments = [record for record in records if record[2] == 3 and record[3] == 2 and int(record[0]) > last_payment_id]
            
            if MC1L1_payments:
                last_payment_id = max(int(record[0]) for record in MC1L1_payments) #Update last_payment_id to Max id from payment records processed.
                payments_data['last_payment_id'] = last_payment_id
                payments_data['available_balance'] = round(sum(float(record[4]) for record in MC1L1_payments) + available_balance, 2)
                payments_data['date_processed'] = datetime.now().strftime('%Y-%m-%d [%H:%M:%S]')
                try:
                    access_app_data('w', logger, app_data) # See file_paths.py
                except Exception as e:
                    logger.exception("Unable to access app data in write mode")
            else:
                pass
        else:
            pass
        
    except Exception as e:
        logger.error(f"An error occured while processing imflow: {e}")
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")
