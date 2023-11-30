from mysql_pool import POOL
import datetime
from datetime import datetime


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
get_records_from_mc_inflow = """select 
ID, Date, Description, Amount, Type, LandlordID, PropertyID, StatementID 
from MC_inflow 
where Date >= %s;
"""


def get_landlord_inflow(pool, inf_monthstart):
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
        cursor.execute(insert_mc_inflow, (inf_monthstart,))
        cursor.execute(update_mc_inflow)
        cursor.execute(get_records_from_mc_inflow, (inf_monthstart,))
        records = cursor.fetchall()

        # Initializing list with default values so I dont get a nonetype error if the record is empty
        MC1L1_SC_NSC_MGT_list = [0,0,0,0]
        MC2L1_SC_NSC_MGT_list = [0,0,0,0]
        MC2L2_SC_NSC_MGT_list = [0,0,0,0]
        MC2L3_SC_NSC_MGT_list = [0,0,0,0]

        if records:
    
            MC1L1_SC    = [record for record in records if record[6] == 1 and record[5] == 1 and record[4] == 'SC']
            MC1L1_NSC   = [record for record in records if record[6] == 1 and record[5] == 1 and record[4] == 'NSC']
            MC1L1_MGT   = [record for record in records if record[6] == 1 and record[5] == 1 and record[4] == 'MGT']
           
            mnth_MC1L1_SC = round(float(sum(record[3] for record in MC1L1_SC if record[1] >= datetime.now().date().replace(day=1))),2)
            all_MC1L1_SC = round(float(sum(record[3] for record in MC1L1_SC)),2)
            sum_MC1L1_NSC = round(float(sum(record[3] for record in MC1L1_NSC)),2)
            curr_MC1L1_MGT = round(float(sum(record[3] for record in MC1L1_MGT if record[1] >= datetime.now().date().replace(day=1))),2) # Checks for payment within current month

            MC2L1_SC    = [record for record in records if record[6] == 2 and record[5] == 1 and record[4] == 'SC']
            MC2L1_NSC   = [record for record in records if record[6] == 2 and record[5] == 1 and record[4] == 'NSC']
            MC2L1_MGT   = [record for record in records if record[6] == 2 and record[5] == 1 and record[4] == 'MGT']
           
            mnth_MC2L1_SC = round(float(sum(record[3] for record in MC2L1_SC if record[1] >= datetime.now().date().replace(day=1))),2)
            all_MC2L1_SC = round(float(sum(record[3] for record in MC2L1_SC)),2)
            sum_MC2L1_NSC = round(float(sum(record[3] for record in MC2L1_NSC)),2)
            curr_MC2L1_MGT = round(float(sum(record[3] for record in MC2L1_MGT if record[1] >= datetime.now().date().replace(day=1))),2) # Checks for payment within current month

            MC2L2_SC    = [record for record in records if record[6] == 2 and record[5] == 2 and record[4] == 'SC']
            MC2L2_NSC   = [record for record in records if record[6] == 2 and record[5] == 2 and record[4] == 'NSC']
            MC2L2_MGT   = [record for record in records if record[6] == 2 and record[5] == 2 and record[4] == 'MGT']
            
            mnth_MC2L2_SC = round(float(sum(record[3] for record in MC2L2_SC if record[1] >= datetime.now().date().replace(day=1))),2)
            all_MC2L2_SC = round(float(sum(record[3] for record in MC2L2_SC)),2)
            sum_MC2L2_NSC = round(float(sum(record[3] for record in MC2L2_NSC)),2)
            curr_MC2L2_MGT = round(float(sum(record[3] for record in MC2L2_MGT if record[1] >= datetime.now().date().replace(day=1))),2) # Checks for payment within current month

            MC2L3_SC    = [record for record in records if record[6] == 2 and record[5] == 3 and record[4] == 'SC']
            MC2L3_NSC   = [record for record in records if record[6] == 2 and record[5] == 3 and record[4] == 'NSC']
            MC2L3_MGT   = [record for record in records if record[6] == 2 and record[5] == 3 and record[4] == 'MGT']
           
            mnth_MC2L3_SC = round(float(sum(record[3] for record in MC2L3_SC if record[1] >= datetime.now().date().replace(day=1))),2)
            all_MC2L3_SC = round(float(sum(record[3] for record in MC2L3_SC)),2)
            sum_MC2L3_NSC = round(float(sum(record[3] for record in MC2L3_NSC)),2)
            curr_MC2L3_MGT = round(float(sum(record[3] for record in MC2L3_MGT if record[1] >= datetime.now().date().replace(day=1))),2) # Checks for payment within current month

            MC1L1_SC_NSC_MGT_list = [mnth_MC1L1_SC, all_MC1L1_SC, sum_MC1L1_NSC, curr_MC1L1_MGT]
            MC2L1_SC_NSC_MGT_list = [mnth_MC2L1_SC, all_MC2L1_SC, sum_MC2L1_NSC, curr_MC2L1_MGT]
            MC2L2_SC_NSC_MGT_list = [mnth_MC2L2_SC, all_MC2L2_SC, sum_MC2L2_NSC, curr_MC2L2_MGT]
            MC2L3_SC_NSC_MGT_list = [mnth_MC2L3_SC, all_MC2L3_SC, sum_MC2L3_NSC, curr_MC2L3_MGT]

            inflow_records = [MC1L1_SC_NSC_MGT_list, MC2L1_SC_NSC_MGT_list, MC2L2_SC_NSC_MGT_list, MC2L3_SC_NSC_MGT_list]
            
        return inflow_records
        
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")

pool = POOL
inf_monthstart = datetime.now().replace(day=1)
get_landlord_inflow(pool, inf_monthstart)