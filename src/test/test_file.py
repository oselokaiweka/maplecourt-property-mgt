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

"""

record1 = 'oseloka is a boy'
record2 = 'oseloka is not a girl'
record3 = 'chinedu is my name'

records = [record1, record2, record3]

filters = ['a', 'is']

filtered = [record for record in records if any(filter not in record.split() for filter in filters)]

for filter in filtered:
    print(filter)

"""


def max_subarray(array):    
    max_sum = float('-inf')
    current_sum = 0

    for num in array:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)

    return max_sum
    

array = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
print(max_subarray(array))

def max_subarray(array):
    max_sum = float('-inf')
    current_sum = 0
    start_index = 0
    end_index = 0
    temp_start_index = 0

    for i in range(len(array)):
        current_sum += array[i]

        if current_sum < 0:
            current_sum = 0
            temp_start_index = i + 1

        if current_sum > max_sum:
            max_sum = current_sum
            start_index = temp_start_index
            end_index = i

    subarray = array[start_index:end_index + 1]
    return max_sum, subarray

array = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
max_sum, max_subarray_values = max_subarray(array)

print("Maximum Subarray Sum:", max_sum)
print("Elements of the Maximum Subarray:", max_subarray_values)