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
    def __init__(self, last_payment_id, available_balance, diesel_contribution) -> None:
        self.last_payment_id = last_payment_id
        self.available_balance = available_balance
        self.diesel_contribution = diesel_contribution

class Rates: 
    def __init__(self, service_charge) -> None:
        self.service_charge = service_charge


def pay_bill(bill, payment_purse, rates):
    bill.balance_brought_f = bill.outstanding # Update app data balance brought forward to equal previous outstanding.

    if bill.bill_name != 'service_charge':
        bill.outstanding = bill.bill_total + bill.balance_brought_f # Update bill outstanding to sum of current bill total and balance brought forward.

        if payment_purse.available_balance >= bill.outstanding: # If payment purse balance is more than or equal to outstanding bill, then deduct full outstanding from payment purse...
            
            payment_purse.available_balance -= bill.outstanding # Deduct full outstanding from payment purse.
            bill.outstanding = 0.0 # Outstanding becomes empty.
            
        else: # If payment purse is insufficient to clear outstanding then deduct entire payment purse balance from outstanding...

            bill.outstanding -= payment_purse.available_balance # Deduct entire payment purse balance from outstanding.
            payment_purse.available_balance = 0.0 # Empty payment purse accordingly. 

    else:
        if payment_purse.available_balance >= rates.service_charge: # If payment purse balance is more than or equal to monthly service charge, deduct full servce charge from payment purse...
        
            # New outstanding = current bill total, PLUS previous outstanding, LESS full service charge, LESS diesel contribution.
            bill.outstanding = round(bill.bill_total + bill.balance_brought_f - rates.service_charge - payment_purse.diesel_contribution, 2)
            bill.amount_paid = round(rates.service_charge, 2) # Update amount_paid to equal full service charge deducted from payment_purse.
            payment_purse.available_balance -= rates.service_charge # Deduct full service charge from purse.
    
        else: # If purse balance is LESS than monthly service charge... 
            
            # New outstanding = current bill total, PLUS previous outstanding, LESS entire payment purse balance, LESS diesel contribution.
            bill.outstanding = round(bill.bill_total + bill.balance_brought_f - payment_purse.available_balance - payment_purse.diesel_contribution, 2)
            bill.amount_paid = round(payment_purse.available_balance, 2) # Set amount_paid to equal balance in payment_purse.
            payment_purse.available_balance = 0.0 # Empty payment purse accordingly.

    
            

def mc1_settle_bill(logger_instance):
    app_data, payments, bills, rates = get_figures(logger_instance)

    logger_instance.info(f"Processing MC1 expenses for {bills['mgt']['bill_start_date']} tot {bills['mgt']['bill_stop_date']}")

    payment_purse = Payment_purse(payments['last_payment_id'], payments['available_balance'], payments['diesel_contribution'])
    rates = Rates(rates['prev_service_charge'])
    for category_bill, bill_detail in bills.items():
        bill = Bill(bill_detail['bill_name'], bill_detail['bill_total'], bill_detail['balance_brought_f'], bill_detail['bill_outstanding'], bill_detail['amount_paid'], bill_detail['last_payment_id'])

        if payment_purse.last_payment_id > bill.last_payment_id:
            logger_instance.info(f"Processing payment for {bill.bill_name.upper()}:\n\nCurrent Bill Total: {bill.bill_total:,.2f}\nPrevious outstanding: {bill.outstanding:,.2f}\n\n")
            try:
                pay_bill(bill, payment_purse, rates)

                bill_detail['bill_outstanding'] = round(bill.outstanding, 2)
                bill_detail['last_payment_id'] = bill.last_payment_id
                bill_detail['date_processed'] = bill.date_processed
                bill_detail['amount_paid'] = bill.amount_paid
                payments['available_balance'] = round(payment_purse.available_balance, 2)

                if payment_purse.available_balance == 0.0:
                    logger_instance.info(f"\nPayment of {bill.bill_name.upper()}: PART  /  Outstanding bill: N{bill.outstanding:.2f}  /  Purse balance: N{payment_purse.available_balance:,.2f}  /  Payment id: {payment_purse.last_payment_id}")     
                else:
                    logger_instance.info(f"\nPayment of {bill.bill_name.upper()}: FULL  /  Outstanding bill: N{bill.outstanding:.2f}  /  Purse balance: N{payment_purse.available_balance:,.2f}  /  Payment id: {payment_purse.last_payment_id}")
                
            except Exception as e:
                logger_instance.exception(f"An error occured while processng {bill.bill_name}: {e}")
        else:
            logger_instance.info('No new payment to be processed.')
            continue

    access_app_data('w', logger_instance, app_data)
    logger_instance.info("Bill processing complete")
