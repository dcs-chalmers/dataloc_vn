## create the data for the plot showing the query response times for all valid queries

import sys
sys.path.append('../../')
sys.path.append('../')
from sim import *
import time
import os

defaultalpha = 1.25
defaultbeta = 0.7

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")
parser.add_argument("-a", "--alpha", default=defaultalpha, type=float, help=f"Choose value for alpha. Default: {defaultalpha}")
parser.add_argument("-b", "--beta", default=defaultbeta, type=float, help=f"Choose value for beta. Default: {defaultbeta}")
parser.add_argument("repetitions", type=int, help="Choose the number of repetitions.")

args = parser.parse_args()


print(f"Running static simulation, 1000 reps, with parameters:")
print(f"\n{args.__dict__}")


##### parameters chosen: ####

alpha = args.alpha # value in paper
beta  = args.beta  # value in paper

experiment = args.experiment
reps = args.repetitions

#############################

algos = {"balanced" : BalancedAlgo(alpha=alpha,beta=beta),
		"fair" 		: FairAlgo(alpha=alpha,beta=beta),
		"baseline1" : Baseline1(),
		"baseline2" : Baseline2()}

##### set comm. latency #####

from wireless_latencies import Ofcom2014_gamma as Ofc
latency_generator = Ofc()
latency = latency_generator.get_sampler()



dirName = 'alpha={}_beta={}_{}_all_algos_shortqueries'.format(alpha,beta,experiment)
if not os.path.exists(dirName):
    os.mkdir(dirName)

for algoname in algos.keys():

	thealgo = lambda : simbeijing(algos[algoname], latency=latency) 
	filename = dirName + "/" + "sim_{}_short_".format(experiment) + algoname + "_alpha=" + str(alpha) + "_beta=" + str(beta)
	repeat_simulation(thealgo, filename, m=reps)
	print(f"done {algoname}")
