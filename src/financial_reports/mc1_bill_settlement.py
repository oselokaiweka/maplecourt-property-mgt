from datetime import datetime

from src.utils.my_logging import mc_logger
from src.utils.file_paths import access_app_data

def get_figures(logger_instance):
    app_data = access_app_data('r', logger_instance)
    payments = app_data['payments']
    bills = app_data['bills']
    rates = app_data['rates']
    return app_data, payments, bills, rates

class Bill:
    def __init__(self, bill_name, bill_total, balance_brought_f, outstanding, amount_paid, last_payment_id ) -> None:
        self.bill_name = bill_name
        self.bill_total = bill_total
        self.balance_brought_f = balance_brought_f
        self.outstanding = outstanding
        self.amount_paid = amount_paid
        self.last_payment_id = last_payment_id
        self.date_processed = datetime.now().strftime('%Y-%m-%d [%H:%M:%S]')

class Payment_purse:
    def __init__(self, last_payment_id, available_balance, diesel_contribution, tenant_sc) -> None:
        self.last_payment_id = last_payment_id
        self.available_balance = available_balance
        self.diesel_contribution = diesel_contribution
        self.tenant_sc = tenant_sc

class Rates: 
    def __init__(self, service_charge, service_charge_deficit) -> None:
        self.service_charge = service_charge
        self.service_charge_deficit = service_charge_deficit


def pay_bill(bill, payment_purse, rate):
    payment_purse.available_balance += payment_purse.tenant_sc # Add tenant_sc (if any) to payment_purse available_balance.
    payment_purse.tenant_sc = 0.0 # Empty tenant_sc.

    if bill.bill_name != 'service_charge':
        bill.outstanding += bill.balance_brought_f # Update bill outstanding to sum of bill outstanding and balance_brought_f (total payable).

        if payment_purse.available_balance >= bill.outstanding: # If payment purse balance is more than or equal to outstanding bill, then deduct full outstanding from payment purse...
            
            payment_purse.available_balance -= bill.outstanding # Deduct full outstanding from payment purse.
            bill.amount_paid = bill.outstanding # Set amount_paid to equal total outstanding.
            bill.outstanding = 0.0 # Outstanding becomes empty.
            
        else: # If payment purse is insufficient to clear outstanding then deduct entire payment purse balance from outstanding...

            bill.outstanding -= payment_purse.available_balance # Deduct entire payment purse balance from outstanding.
            bill.amount_paid = payment_purse.available_balance # Set amount_paid to equal balance in payment_purse.
            payment_purse.available_balance = 0.0 # Empty payment purse accordingly. 

    else:
        bill.balance_brought_f = bill.outstanding # Update app data balance brought forward to equal previous outstanding.
        if payment_purse.available_balance >= (rate.service_charge + rate.service_charge_deficit): # If payment purse balance is more than or equal to monthly service charge, deduct full servce charge from payment purse...
        
            # New outstanding = current bill total, PLUS previous outstanding, LESS full service charge, LESS diesel contribution.
            bill.outstanding = round(bill.bill_total + bill.balance_brought_f - (rate.service_charge + rate.service_charge_deficit) - payment_purse.diesel_contribution, 2)
            bill.amount_paid = round((rate.service_charge + rate.service_charge_deficit), 2) # Update amount_paid to equal full service charge deducted from payment_purse.
            payment_purse.available_balance -= (rate.service_charge + rate.service_charge_deficit) # Deduct full service charge from purse.
            rate.service_charge_deficit = 0.0

        else: # If purse balance is LESS than monthly service charge... 
            
            # New outstanding = current bill total, PLUS previous outstanding, LESS entire payment purse balance, LESS diesel contribution.
            bill.outstanding = round(bill.bill_total + bill.balance_brought_f + rate.service_charge_deficit - payment_purse.available_balance - payment_purse.diesel_contribution, 2)
            bill.amount_paid = round(payment_purse.available_balance, 2) # Set amount_paid to equal balance in payment_purse.
            rate.service_charge_deficit = (rate.service_charge + rate.service_charge_deficit - bill.amount_paid)
            payment_purse.available_balance = 0.0 # Empty payment purse accordingly.

    
            

def mc1_settle_bill(logger_instance):
    app_data, payments, bills, rates = get_figures(logger_instance)

    logger_instance.info(f"Processing MC1 expenses for [{bills['mgt']['bill_start_date']}]  to  [{bills['mgt']['bill_stop_date']}]")

    payment_purse = Payment_purse(payments['last_payment_id'], payments['available_balance'], payments['diesel_contribution'], payments['tenant_sc'])
    rate = Rates(rates['prev_service_charge'], rates['service_charge_deficit'])
    for category_bill, bill_detail in bills.items():
        bill = Bill(bill_detail['bill_name'], bill_detail['bill_total'], bill_detail['balance_brought_f'], bill_detail['bill_outstanding'], bill_detail['amount_paid'], bill_detail['last_payment_id'])

        if payment_purse.last_payment_id > bill.last_payment_id:
            logger_instance.info(f"\nProcessing payment for {bill.bill_name.upper()}....\nCurrent Bill Total: {bill.bill_total:,.2f}\nPrevious outstanding: {bill.outstanding:,.2f}")
            try:
                pay_bill(bill, payment_purse, rate)

                bill_detail['bill_outstanding'] = round(bill.outstanding, 2)
                bill_detail['last_payment_id'] = payment_purse.last_payment_id
                bill_detail['date_processed'] = bill.date_processed
                bill_detail['balance_brought_f'] = bill.balance_brought_f
                bill_detail['amount_paid'] = round(bill.amount_paid, 2)
                payments['available_balance'] = round(payment_purse.available_balance, 2)
                payments['tenant_sc'] = round(payment_purse.tenant_sc, 2)
                rates['service_charge_deficit'] = round(rate.service_charge_deficit, 2)

                if payment_purse.available_balance == 0.0:
                    logger_instance.info(f"Payment of {bill.bill_name.upper()}: PART  /  Outstanding bill: N{bill.outstanding:.2f}  /  Purse balance: N{payment_purse.available_balance:,.2f}  /  Payment id: {payment_purse.last_payment_id}\n")     
                else:
                    logger_instance.info(f"Payment of {bill.bill_name.upper()}: FULL  /  Outstanding bill: N{bill.outstanding:.2f}  /  Purse balance: N{payment_purse.available_balance:,.2f}  /  Payment id: {payment_purse.last_payment_id}\n")
                
            except Exception as e:
                logger_instance.exception(f"An error occured while processng {bill.bill_name}: {e}")
        else:
            logger_instance.info('No new payment to be processed.')
            continue
    logger_instance.info("\nUpdatng app data...")

    access_app_data('w', logger_instance, app_data)
    logger_instance.info("Update complete")
