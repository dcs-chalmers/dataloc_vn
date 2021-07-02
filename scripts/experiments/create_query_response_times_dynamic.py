## create the data for the plot showing the DYNAMIC query response times for all valid queries

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


print(f"Running dynamic simulation, 1000 reps, with parameters:")
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



dirName = 'alpha={}_beta={}_{}_all_algos_dynamic'.format(alpha,beta,experiment)
if not os.path.exists(dirName):
    os.mkdir(dirName)

for algoname in algos.keys():

	filename = dirName + "/" + "sim_{}_dynamic_".format(experiment) + algoname + "_alpha=" + str(alpha) + "_beta=" + str(beta)
	if experiment == "beijing":
		simbeijing_dynamic(algos[algoname], filename, reps)
	print(f"done {algoname}")