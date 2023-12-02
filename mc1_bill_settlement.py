import os, json
from datetime import datetime
from mysql_pool import POOL

dir_path = os.environ.get('DIR_PATH')

class Bill:
    def __init__(self, name, amount, bill_date) -> None:
        self.name = name
        self.amount = amount
        self.bill_date = bill_date
        self.outstanding = amount

class Received:
    def __init__(self, id, amount, pay_date) -> None:
        self.id = id
        self.amount = amount
        self.pay_date = pay_date
        self.balance = amount

def pay_bill(bill, received):
    if received.balance >= bill.outstanding:
        # If payment is sufficient, settle the entire bill
        print(f"Settling {bill.name} with {received.id} (N{bill.outstanding:,.2f})")
        received.balance -= bill.outstanding
        bill.outstanding = 0.0
    else:
        # If payment is not sufficient, make a partial payment
        print(f"Part payment of N{received.balance:,.2f} for {bill.name}") 
        bill.outstanding -= received.balance
        received.balance = 0