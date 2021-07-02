# generate values for the fairness simulations

import sys
sys.path.append('../../')
from sim import *
import time


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")
parser.add_argument("repetitions", type=int, help="Choose the number of repetitions.")

args = parser.parse_args()

##############################

experiment = args.experiment
reps = args.repetitions

##### set comm. latency #####

from wireless_latencies import Ofcom2014_gamma as Ofc
latency_generator = Ofc()
latency = latency_generator.get_sampler()


#############

def simfunction(algo):
    if experiment == "beijing":
        return simfairnessbeijing(algo, tfile='time.dat', qfile='q.dat', latency=latency)

outfilename = "fairness.csv"



#############


start_time = time.time()
print(f'Starting running...' )

# Baseline1 uses a separate function, since it only needs to be run once
# (the standard deviation of workloads is deterministic)
fairness_simulation_baseline1(outfilename="baseline1" + outfilename, simfunction=simfunction)

# 1000 reps of the three other algorithms
repeat_fairness_simulation(nb_simulations=reps, outfilename=outfilename, simfunction=simfunction)



print('...done in {} hrs'.format((time.time() - start_time)/3600))

