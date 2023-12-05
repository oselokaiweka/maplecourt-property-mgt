import os, json
from datetime import datetime
from mysql_pool import POOL

dir_path = os.environ.get('DIR_PATH')

with open(dir_path+"/mc_app_data.json", "r") as app_data_file:
    app_data = json.load(app_data_file)
payments = app_data['payments']
bills = app_data['bills']
rates = app_data['rates']

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

def pay_bill(bill, received):
    if bill.bill_name == 'service_charge':
        if received.available_balance >= rates['service_charge']:
            # If payment is sufficient, settle the entire bill
            received.available_balance -= rates['service_charge']
            print(f"Settled {bill.bill_name} bill of N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N{received.available_balance:,.2f}")
            bill.outstanding -= rates['service_charge']
            bills['sc']['received'] = round(rates['service_charge'], 2)
        else:
            # If payment is not sufficient, make a partial payment
            prev_outstanding = bill.outstanding
            bill.outstanding -= received.available_balance
            print(f"Part payment of N{received.available_balance:,.2f} out of N{prev_outstanding:,.2f} for {bill.bill_name}, outstanding: N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N0.0") 
            received.available_balance = 0.0  
            bills['sc']['received'] = round(received.available_balance, 2)     
    else:   
        if received.available_balance >= bill.outstanding:
            # If payment is sufficient, settle the entire bill
            received.available_balance -= bill.outstanding
            print(f"Settled {bill.bill_name} bill of N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N{received.available_balance:,.2f}")
            bill.outstanding = 0.0
        else:
            # If payment is not sufficient, make a partial payment
            prev_outstanding = bill.outstanding
            bill.outstanding -= received.available_balance
            print(f"Part payment of N{received.available_balance:,.2f} out of N{prev_outstanding:,.2f} for {bill.bill_name}, outstanding: N{bill.outstanding:,.2f}. Recieved id-{received.last_payment_id} balance: N0.0") 
            received.available_balance = 0.0


def mc1_bill_settlement():
    for bill_key, category in bills.items():
        bill = Bill(category['bill_name'], category['bill_total'], category['bill_outstanding'])
        received = Received(payments['last_payment_id'], payments['available_balance'])
        if bill.outstanding > 0 and received.last_payment_id > category['last_payment_id']:
            try:
                pay_bill(bill, received)
                category['bill_outstanding'] = round(bill.outstanding, 2)
                category['last_payment_id'] = received.last_payment_id
                category['date_processed'] = bill.date_processed
                payments['available_balance'] = round(received.available_balance, 2)
            except (ValueError, TypeError) as e:
                print(e)
        else:
            print('No new payment or pending bill')
            continue

    with open(dir_path+"/mc_app_data.json", "w") as app_data_file:
        json.dump(app_data, app_data_file, indent=4)
