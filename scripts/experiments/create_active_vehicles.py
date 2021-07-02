## create the data for the plot showing the DYNAMIC query response times for all valid queries

import sys
sys.path.append('../../')
sys.path.append('../')

from churn import *

defaultalpha = 1.25
defaultbeta = 0.7

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")

args = parser.parse_args()



#############################


print("Start writing the active vehicle periods...")

write_active_time(folder=beijing_folder, filename="vehicles.dat", delta=15)

print("...done")