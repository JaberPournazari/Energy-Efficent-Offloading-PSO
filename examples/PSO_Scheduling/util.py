import csv,os

import numpy as np
from matplotlib import pyplot as plt



def read_data(datatype):
    with open(datatype.lower() + '.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def write_data(datatype, row):
    fullfilename=datatype.lower() + '.csv'
    dirname=os.path.dirname(fullfilename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    # open the file in the write mode
    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(row)



def write_to_csv(node_energies,filename):
    # save results into csv file before plotting
    power_values = node_energies
    # Extract dynamic and static power values
    dynamic_power = [p.dynamic for p in power_values]
    static_power = [p.static for p in power_values]

    write_data(f'ResultsCsv/{filename}-dynamic', [f"{i:.3f}" for i in dynamic_power])
    write_data(f'ResultsCsv/{filename}-static', [f"{i:.3f}" for i in static_power])

def write_total_power(node_energies,filename,devices_len):
    dynamic_power = [p.dynamic for p in node_energies]
    static_power = [p.static for p in node_energies]
    total_power = sum(dynamic_power) + sum(static_power)
    write_data(f'ResultsCsv/{filename}-total', [devices_len,total_power])

def write_total(sum_time,filename,devices_len):
    write_data(f'ResultsCsv/{filename}-total', [devices_len,sum_time])


