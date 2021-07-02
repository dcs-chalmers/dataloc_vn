# generate values for the estimations simulations

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

def simnfunction(algo, n):
    return simnbeijing(algo, n, tfile='time.dat', qfile='q.dat', latency=latency)

outfilename = "error.csv"

# define ground truths for the estimations. They are defined in sim.py
qbase = qbeijing

#############


start_time = time.time()
print(f'Starting running...' )


repeat_estimation_simulation(nb_simulations=reps, outfilename=outfilename, simfunction=simnfunction, qbase=qbase)


print('...done in {} hrs'.format((time.time() - start_time)/3600))

