# This script retrieves MC1NSC records from two maplecourt database tables that contain 
# all business transactions.
from datetime import datetime, timedelta

from src.utils.credentials import get_cursor
from src.utils.file_paths import access_app_data


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

# Query to retrieve relevant records for specified period.
retrieve_mgtfee_records = """
select U.UnitCode, concat(T.FirstName,' ',T.LastName) as Tenant, 
R.StartDate as 'Rent Start', R.StopDate as 'Rent Stop', U.CurrentRent 
from Rentals R inner join Tenants T on T.TenantID = R.TenantID
inner join Units U on U.UnitID = R.UnitID
where R.UnitCode like 'MC1%'
and R.StopDate > %s
order by U.UnitCode;
"""

# Calculating mgt period in days
def get_mgt_period(rentstart_str, rentstop_str, period_start, period_stop, logger_instance):
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

def days_in_year_function(mgt_start, logger_instance):
    days_in_year = 366 if mgt_start.year % 4 == 0 and (mgt_start.year % 100 != 0 or mgt_start.year % 400 == 0) else 365
    logger_instance.info(f"Days in year is {days_in_year} days")
    return days_in_year

def mc1_mgt_report(pool, mgt_start, mgt_stop, logger_instance):
    # Obtain pool connection if available or add connection then obtain pool connection.
    connection, cursor = get_cursor(pool, logger_instance)

    # Start MySQL event scheduler so any trigger affected by this operation will execute. 
    cursor.execute("SET GLOBAL event_scheduler = ON;")
    logger_instance.info("Event scheduler is started")
    
    # Retrieve relevant fixed values from mc_app_data.json file
    try:
        app_data = access_app_data('r', logger_instance)
        mgt_net_summary = app_data['bills']['mgt']
        mgt_fee_percent = app_data['rates']['mgt_fee_%']
    except Exception as e:
        logger_instance.exception("Unable to load app data")
    
    # Mgt period start & stop gives the option of specifiying dates or None (default) values in the main function call.
    # If None values then current month start and end date will be used. Convert to date objects to avoid incomplete day count. 
    mgt_start = datetime.strptime(mgt_start, '%Y-%m-%d') if mgt_start is not None else datetime.now().replace(day=1)
    month_end = datetime(mgt_start.year + (1 if mgt_start.month == 12 else 0), (mgt_start.month + 1) % 12 if mgt_start.month != 11 else 12, 1) - timedelta(days=1) # Calculates month end
    mgt_stop = datetime.strptime(mgt_stop, '%Y-%m-%d') if mgt_stop is not None else month_end
    
    # create variable to hold table data as list of lits with the first being the header
    mgtfee_table_data = [['UNIT', 'TENANT', 'RENT START', 'RENT STOP', 'RENT(N)', 'FEE/DAY', 'DAYS', 'MGT FEE(N)']]
    total_mgt_fee = 0
    days_in_year = days_in_year_function(mgt_start, logger_instance)

    try: 
        cursor.execute(update_rentals_stopdate)
        cursor.execute(update_rentals_rentstatus)
        cursor.execute(retrieve_mgtfee_records, (mgt_start,))
        records = cursor.fetchall()
        
        if records:
            logger_instance.info("Records have been retrieved, ready for processing.\n")

            logger_instance.info(F"{'UNIT':5}  :  {'TENANT':17}  :  {'RENT START':10}  :  {'RENT STOP':10}  : {'RENT PRICE':11} : {'RENT/DAY':6} : {'DAYS':2} :   {'MGT FEE':11}")
            logger_instance.info("----------------------------------------------------------------------------------------------------------")

            for record in records:
                unit, tenant, rentstart, rentstop, rentprice = record[:5]            
                rentstart_str = (datetime.strptime(str(rentstart), '%Y-%m-%d')) # Convert date strings to date objects         
                rentstop_str = (datetime.strptime(str(rentstop), '%Y-%m-%d')) # Convert date strings to date objects 
                
                period = get_mgt_period(rentstart_str, rentstop_str, mgt_start, mgt_stop, logger_instance)
            
                if period > 0: # 0 period indicates inactive rent and will be omitted by the continue in else clause.
                    mgtfee_per_day = (rentprice * mgt_fee_percent / 100) / days_in_year # Calculating mgt fee per day
                    mgtfee_for_period = mgtfee_per_day * period # Calculating mgt fee for the period
                    total_mgt_fee += mgtfee_for_period # Calculating total mgt fee
                    rentprice = f"{rentprice:,.0f}" # Formatting digits
                    mgtfee_per_day = f"{mgtfee_per_day:,.2f}" # Formatting digits
                    mgtfee_for_period = f"{mgtfee_for_period:,.2f}" # Formatting digits
                
                    mgtfee_table_data.append([unit, tenant, rentstart, rentstop, rentprice, mgtfee_per_day, period, mgtfee_for_period])

                    logger_instance.info(f"{unit:5}  :  {tenant:17}  :  {rentstart}  :  {rentstop}  :  {rentprice:9}  :  {mgtfee_per_day:6}  :  {period:2}  :   {mgtfee_for_period:11}")
                else:
                    continue

            logger_instance.info("----------------------------------------------------------------------------------------------------------")

            logger_instance.info(f"{'Total management fee':89}  :  {total_mgt_fee:10,.2f}\n") # Formatting digits

            # Updating app data json file.
            try:
                # Update json file if mgt_start is after app data stop date to avoid duplicate processing
                if mgt_start > datetime.strptime(mgt_net_summary['bill_stop_date'], '%Y-%m-%d'):
                    mgt_net_summary['balance_brought_f'] = mgt_net_summary['bill_outstanding'] # Push any outstanding from previous payment processing to balance_brought_f.
                    mgt_net_summary['bill_outstanding'] = mgt_net_summary['bill_total'] # Set bill outstanding to last months bill total ready for received payment processing.
                    mgt_net_summary['bill_total'] = round(total_mgt_fee,2) # New bill total will be processed with payment of new invoice being created.
                    mgt_net_summary['bill_start_date'] = mgt_start.strftime('%Y-%m-%d')
                    mgt_net_summary['bill_stop_date'] = mgt_stop.strftime('%Y-%m-%d')

                    access_app_data('w', logger_instance, app_data)
                else:
                    logger_instance.info("Report for the period has been processed already.")

            except Exception as e:
                logger_instance.exception("Unable to dump app data to file")

            return mgtfee_table_data
        else:
            logger_instance.info("No record found")
            # Update json file if mgt_start is after app data stop date to avoid duplicate processing
            if mgt_start > datetime.strptime(mgt_net_summary['bill_stop_date'], '%Y-%m-%d'):
                mgt_net_summary['balance_brought_f'] = mgt_net_summary['bill_outstanding'] # Push any outstanding from previous payment processing to balance_brought_f.
                mgt_net_summary['bill_outstanding'] = mgt_net_summary['bill_total'] # Set bill outstanding to last months bill total ready for received payment processing.
                mgt_net_summary['bill_total'] = 0.0 # New bill total will be processed with payment of new invoice being created.
                mgt_net_summary['bill_start_date'] = mgt_start.strftime('%Y-%m-%d')
                mgt_net_summary['bill_stop_date'] = mgt_stop.strftime('%Y-%m-%d')

                access_app_data('w', logger_instance, app_data)
            else:
                logger_instance.info("Report for the period has been processed already.")
            return mgtfee_table_data
    except Exception as e:
        logger_instance.exception("An error occurred while processing nsc report: {e}")
    finally:
        #Close cursor
        cursor.close()
        connection.close()
        logger_instance.info("Connection and cursor closed.\n")
