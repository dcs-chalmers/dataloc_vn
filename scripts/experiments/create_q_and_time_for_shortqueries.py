#!/usr/bin/env python3

# python3 scriptname.py beijing path_to_daysfolder path_to_basefolder

import sys
sys.path.append('../../')
sys.path.append('../datasets/')
import time
from query import *
import paths


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to run.")

args = parser.parse_args()

mode       = args.experiment
basefolder = paths.beijing_folder


### actually execute

start_time = time.time()

print("Calculating answer behavior and workload per vehicle...".format(mode))

if mode == "beijing":
	gen_beijing_timeq_files(basefolder)
else:
	print("This should never have happened. I quit.")
	quit()

time_needed = time.time() - start_time

print("...done in {} hrs".format(time_needed/3600))
