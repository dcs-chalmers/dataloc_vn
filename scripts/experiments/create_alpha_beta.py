# generate values for the alpha-beta-plot, which runs the simulator over the beijing queries
# for different values of alpha and beta for the balanced algorithm

import sys
sys.path.append('../../')
from sim import *
import time
import os
from progress_bar import update_progress

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")
parser.add_argument("repetitions", type=int, help="Choose the number of repetitions.")

args = parser.parse_args()

##############################

alphas = [0.25*i+0.25 for i in range(8)] 
betas = [0.1*i+0.1 for i in range(10)]

experiment = args.experiment
reps = args.repetitions

##### set comm. latency #####

from wireless_latencies import Ofcom2014_gamma as Ofc
latency_generator = Ofc()
latency = latency_generator.get_sampler()



dirName = f'alpha_beta_{experiment}_balancedAlgo_shortqueries'
if not os.path.exists(dirName):
    os.mkdir(dirName)


start_time = time.time()
print(f'Starting running the simulator for BalancedAlgo, {experiment} (short queries)...' )

num_processing_steps = len(alphas) * len(betas)

counter = 0
for alpha in alphas:
    for beta in betas:
        update_progress(counter/num_processing_steps)
        thealgo = lambda : simbeijing(BalancedAlgo(alpha=alpha, beta=beta), latency=latency) 
        filename = dirName + "/" + f"sim_{experiment}_short_BalancedAlgo_alpha=" + str(alpha) + "_beta=" + str(beta)
        repeat_simulation(thealgo, filename, m=reps)
        counter += 1

print('...done in {} hrs'.format((time.time() - start_time)/3600))

