"""
import calendar
from datetime import datetime
import os
import json

grand_total = 100000.00


dir_path = os.environ.get('DIR_PATH')
with open(dir_path+"/sc_net.txt", "r") as net_dictionary:
    net_summary = json.load(net_dictionary)
print(net_summary['curr_net'])
new_net = net_summary['curr_net'] * 2
print(new_net)
"""
"""
curr_net = f'{float(prev_net) + grand_total}'
with open(dir_path+"/sc_net.txt", "w") as curr_net_file:
    curr_net_file.write(curr_net)
"""



record1 = 'oseloka is a boy'
record2 = 'oseloka is not a girl'
record3 = 'chinedu is my name'

records = [record1, record2, record3]

filters = ['a', 'is']

filtered = [record for record in records if any(filter not in record.split() for filter in filters)]

for filter in filtered:
    print(filter)