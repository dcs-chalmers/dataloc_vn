# generate values for the estimations simulations

import sys
sys.path.append('../../')
sys.path.append('../datasets/')
from churn import *


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")

args = parser.parse_args()

##############################

experiment = args.experiment



print(f'Starting running...' )


write_churns(beijing_folder,"beijing")


print('...done')

