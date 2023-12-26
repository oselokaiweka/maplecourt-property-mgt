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
    def __init__(self, bill_name, bill_total, outstanding) -> None:
        self.bill_name = bill_name
        self.bill_total = bill_total
        self.outstanding = outstanding
        self.date_processed = datetime.now().strftime('%Y-%m-%d [%H:%M:%S]')

class Received:
    def __init__(self, last_payment_id, available_balance) -> None:
        self.last_payment_id = last_payment_id
        self.available_balance = available_balance

def pay_bill(bill, received, logger_instance):
    app_data, payments, bills, rates = get_figures(logger_instance)
    if bill.bill_name == 'service_charge':
        if received.available_balance >= rates['prev_service_charge']:
            # If payment is sufficient, settle the entire bill
            received.available_balance -= rates['prev_service_charge']
            bills['sc']['balance_brought_f'] = bill.outstanding
            bill.outstanding = round(bill.bill_total + bills['sc']['balance_brought_f'] - rates['prev_service_charge'] - payments['diesel_contribution'], 2)
            bills['sc']['received'] = round(rates['prev_service_charge'], 2)
            logger_instance.info(f"Settled {bill.bill_name} bill. Recieved id-{received.last_payment_id} balance: N{received.available_balance:,.2f}")
        else:
            # If payment is not sufficient, make a partial payment
            bills['sc']['balance_brought_f'] = bill.outstanding
            bill.outstanding = round(bill.bill_total + bills['sc']['balance_brought_f'] - received.available_balance - payments['diesel_contribution'], 2)
            bills['sc']['received'] = round(received.available_balance, 2)
            received.available_balance = 0.0
            logger_instance.info(f"Part settled {bill.bill_name} bill. Recieved id-{received.last_payment_id} balance: N{received.available_balance:,.2f}")     
    else:   
        if received.available_balance >= bill.outstanding:
            # If payment is sufficient, settle the entire bill
            received.available_balance -= bill.outstanding
            logger_instance.info(f"Settled {bill.bill_name} bill of N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N{received.available_balance:,.2f}")
            bill.outstanding = 0.0
        else:
            # If payment is not sufficient, make a partial payment
            prev_outstanding = bill.outstanding
            bill.outstanding -= received.available_balance
            logger_instance.info(f"Part payment of N{received.available_balance:,.2f} out of N{prev_outstanding:,.2f} for {bill.bill_name}, outstanding: N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N0.0") 
            received.available_balance = 0.0


def mc1_settle_bill(logger_instance):
    app_data, payments, bills, rates = get_figures(logger_instance)
    for bill_key, category in bills.items():
        bill = Bill(category['bill_name'], category['bill_total'], category['bill_outstanding'])
        received = Received(payments['last_payment_id'], payments['available_balance'])
        if (bill.bill_name != 'service_charge' and bill.outstanding > 0 and received.last_payment_id > category['last_payment_id']) or (bill.bill_name == 'service_charge' and received.last_payment_id > category['last_payment_id']):
            try:
                pay_bill(bill, received, logger_instance)
                category['bill_outstanding'] = round(bill.outstanding, 2)
                category['last_payment_id'] = received.last_payment_id
                category['date_processed'] = bill.date_processed
                payments['available_balance'] = round(received.available_balance, 2)
            except (ValueError, TypeError) as e:
                logger_instance.exception(f"An error occured while settling mc1 bill: {e}")
        else:
            logger_instance.info('No new payment or pending bill')
            continue

    access_app_data('w', logger_instance, app_data)
    logger_instance.info("Bill settlement process complete")
