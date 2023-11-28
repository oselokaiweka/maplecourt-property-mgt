# This script retrieves MC1NSC records from two maplecourt database tables that contain 
# all business transactions.
import calendar
from datetime import datetime, timedelta
from mysql_pool import POOL

# Update rent stopdate according to rent paid by tenant
update_rentals_stopdate = """
update Rentals R inner join Units U using (UnitID) 
set R.StopDate = date_add(R.StartDate, interval floor(R.RentPaid / (U.CurrentRent / 12)) month);
"""

# Update RentStatus to either Active or Inactive. 
update_rentals_rentstatus = """
update Rentals set RentStatus = case 
when StopDate < current_date() then 'Inactive'
else 'Active' end;
"""

# Query to retrieve relevant records from mc1 active rentals used for mgt fee calculation.
retrieve_mgtfee_records = """
select U.UnitCode, concat(T.FirstName,' ',T.LastName) as Tenant, 
R.StartDate as 'Rent Start', R.StopDate as 'Rent Stop', U.CurrentRent 
from Rentals R inner join Tenants T on T.TenantID = R.TenantID
inner join Units U on U.UnitID = R.UnitID
where R.UnitCode like 'MC1%'
and R.StopDate > date_format(current_date(), '%Y-%m-01')
order by U.UnitCode;
"""

# Calculating mgt period in days
def get_mgt_period(rentstart_str, rentstop_str, period_start, period_stop):
    # The logic below ensures date difference returns complete days of the month without excess for periods that start mid month.
    if rentstop_str > period_start: # Checks for active rent.
        mgt_period_stop = min(rentstop_str, period_stop) # If rent terminates before end of mgt period, mgt fee is calculated till rent termination.
        if rentstart_str > period_start: # If rent starts after mgt period start then mgt fee is calculated from rent start.
            mgt_period_start = rentstart_str            
            period = (mgt_period_stop - mgt_period_start).days
        else:
            mgt_period_start = period_start
            period = (mgt_period_stop - mgt_period_start).days + 1 # End of month - first of month will be one day short, hence the + 1.
    else:
        period = 0 # In case of expired rent, period is initialized with zero to avoid nonetype error
    return period

def curr_date_and_days_in_year():
    curr_date = datetime.now()
    days_in_year = 366 if curr_date.year % 4 == 0 and (curr_date.year % 100 != 0 or curr_date.year % 400 == 0) else 365
    return curr_date, days_in_year

def mc1_mgt_report(pool, period_start, period_stop):
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
    cursor.execute("SET GLOBAL event_scheduler = ON;")
    print('Event scheduler is started')
    

    # create variable to hold table data as list of lits with the first being the header
    mgtfee_table_data = [['UNIT', 'TENANT', 'RENT START', 'RENT STOP', 'RENT(N)', 'FEE/DAY', 'DAYS', 'MGT FEE(N)']]
    total_mgt_fee = 0
    curr_date, days_in_year = curr_date_and_days_in_year()

    # Calculating mgt fee start and stop dates
    month_start = curr_date.replace(day=1)
    _, month_end = calendar.monthrange(curr_date.year, curr_date.month)
    month_end = datetime(curr_date.year, curr_date.month, month_end)
    
    # Mgt period start & stop gives the option of specifiying dates or None (default) values in the main function call.
    # If None values then current month start and end date will be used. Convert to date objects to avoid incomplete day count. 
    mgt_period_start = (datetime.strptime(period_start, '%Y-%m-%d') if period_start is not None else month_start).date()
    mgt_period_stop = (datetime.strptime(period_stop, '%Y-%m-%d') if period_stop is not None else month_end).date()
    
    try: 
        cursor.execute(update_rentals_stopdate)
        cursor.execute(update_rentals_rentstatus)
        cursor.execute(retrieve_mgtfee_records)
        records = cursor.fetchall()
        
        if records:
            for record in records:
                unit, tenant, rentstart, rentstop, rentprice = record[:5]            
                rentstart_str = (datetime.strptime(str(rentstart), '%Y-%m-%d')).date() # Convert date strings to date objects         
                rentstop_str = (datetime.strptime(str(rentstop), '%Y-%m-%d')).date() # Convert date strings to date objects 
                
                period = get_mgt_period(rentstart_str, rentstop_str, mgt_period_start, mgt_period_stop)
            
                if period > 0: # 0 period indicates inactive rent and will be omitted by the continue in else clause.
                    mgtfee_per_day = (rentprice * .075) / days_in_year # Calculating mgt fee per day
                    mgtfee_for_period = mgtfee_per_day * period # Calculating mgt fee for the period
                    total_mgt_fee += mgtfee_for_period # Calculating total mgt fee
                    rentprice = f"{rentprice:,.0f}" # Formatting digits
                    mgtfee_per_day = f"{mgtfee_per_day:,.2f}" # Formatting digits
                    mgtfee_for_period = f"{mgtfee_for_period:,.2f}" # Formatting digits
                
                    mgtfee_table_data.append([unit, tenant, rentstart, rentstop, rentprice, mgtfee_per_day, period, mgtfee_for_period])
                    print(f'{unit} : {tenant} : {rentstart} : {rentstop} : {rentprice} : {mgtfee_per_day} : {period} : {mgtfee_for_period}')
                else:
                    continue
            total_mgt_fee = f"{total_mgt_fee:,.2f}" # Formatting digits
            return mgtfee_table_data, total_mgt_fee, mgt_period_start
        else:
            print('No record found')
    except Exception as e:
        print(e)
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        print("Connection and cursor closed.\n")
    
if __name__ == '__main__':
    pool = POOL
    period_start = None
    period_stop = None
    mc1_mgt_report(pool, period_start, period_stop)