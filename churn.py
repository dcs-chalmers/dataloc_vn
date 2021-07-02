#!/usr/bin/env python3

## update 2019-08

from os import listdir
from os.path import join, exists, getsize
from os import mkdir
from shutil import copyfile

from math import floor, ceil
from random import choice

from query import *

intervals = lambda nbseconds : int(DAY/nbseconds)

import sys
sys.path.append("scripts/datasets")

try:
    from paths import *
except:
    sys.path.append("../datasets/")
    from paths import *
    

### Dynamic Model ###

def compute_active_periods(trace, delta=5):
    active_periods = []
    if trace: # some traces are empty looks like it...
        start_ts = last_ts = trace[0][0]
        for x in trace:
            t = x[0]
            if t <= last_ts + delta:
                last_ts = t
            else:
                if last_ts > start_ts:
                    active_periods.append((start_ts, last_ts))
                start_ts = last_ts = t
    return active_periods

def compute_active_time_vehicles(folder,delta):
    return [(file, compute_active_periods(load(join(folder,file)),delta)) for file in sorted(listdir(folder)) if getsize(join(folder,file)) > 0]

def write_active_time(folder=beijing_folder, filename="vehicles.dat", delta=15):
    with open(filename, "w") as f:
        for filename,vehicle in compute_active_time_vehicles(folder,delta):
            print(filename, file=f, end=",")
            print(','.join([f"{start},{end}" for start,end in vehicle]), file=f)


# CHURN and diverse stats computation on the datasets

# allow to compute also "churnin" or 'arrival rate'
def compute_churn(folder, nbintervals=1440, churn=True):
    #nbintervals=int(DAY*1000/length)
    cars, churn = [0]*nbintervals, [0]*nbintervals
    offset = 1 if churn else -1

    for filename in sorted(listdir(folder)):
        with open(join(folder,filename), "r") as file:
            intervals = set()
            for line in file.readlines():
                intervals.add( int( float(line.split(",")[0]) / (DAY/nbintervals) ) )
            for interval in intervals:
                cars[interval] += 1
                if (interval+offset)%nbintervals not in intervals:
                    churn[interval] += 1
    return cars, churn

def write_nb_cars(folder, outfilename, nbintervals=1440):
    cars = [0]*nbintervals
    for filename in sorted(listdir(folder)):
        with open(join(folder,filename), "r") as file:
            lastseen = -1
            for line in file.readlines():
                interval = int( float(line.split(",")[0]) / (DAY/nbintervals) )
                if interval > lastseen:
                    cars[interval] += 1
                    lastseen = interval
    with open(outfilename, "w") as outf:
        for i in range(nbintervals):
            print(i, cars[i], file=outf)
          
def write_churn(folder, outfilename, nbintervals=1440, churn=True):
    cars, churn = compute_churn(folder, nbintervals, churn)
    with open(outfilename, "w") as outf:
        for i in range(len(cars)):
            print(i, churn[i], sep=' ', file=outf)

def write_arrival_rate(folder, outfilename, nbintervals=1440):
    write_churn(folder, outfilename, nbintervals, False)

def print_churn(folder, nbintervals=1440):
    cars, churn = compute_churn(folder,nbintervals)
    for i in range(len(churn)):
        if cars[i]:
            print(i*(DAY//nbintervals), cars[i], 100 * churn[i]/cars[i])

def write_average_churn(folder, outfile, length=60, nbbins=100):
    nbintervals = DAY//length
    cars, churn = compute_churn(folder, nbintervals)
    bins = DAY//nbbins
    
    def average_churn(timesec):
        i = timesec//length
        return churn[i]/cars[i] if cars[i] else 0

    def average_cars(timesec):
        return cars[timesec//length]

    binit = lambda f: round(sum(f(j) for j in range(i*bins,(i+1)*bins))/bins, 3)

    for i in range(nbbins-1):
        print(i, binit(average_churn), binit(average_cars), file=outfile)

def write_churns(folder, outfileprefix):
    for length in [10,30,60,120,300,900]:
        outfilename = outfileprefix + "_" + str(length) + ".dat"
        print(outfilename)
        with open(outfilename, 'w') as outfile:
            write_average_churn(folder, outfile, length, 100)

def max_churn(folder, nbintervals=1440):
    cars, churn = compute_churn(folder,nbintervals)
    return max(churn[i]/cars[i] for i in range(len(churn)) if cars[i])

def average_churn(folder, nbintervals=1440):
    cars, churn = compute_churn(folder,nbintervals)
    return sum(churn[i]/cars[i] for i in range(len(churn)) if cars[i])/len(churn)

def max_cars(folder, nbintervals=1440):
    cars, churn = compute_churn(folder,nbintervals)
    return max(cars[i] for i in range(len(cars)))

## inflate date for long queries

def active_vehicles(folder, start=64800, end=65100):
    activefolder = join(datafolder,"active-"+str(start)+"-"+str(end))
    if not exists(activefolder):
        mkdir(activefolder)
    for filename in sorted(listdir(folder)):
        with open(join(folder,filename), "r") as file:
            for line in file.readlines():
                if start <= float(line.split(",")[0]) <= end :
                    copyfile(join(folder,filename), join(activefolder,filename))
                    break

def inflate_data(basefolder, activefolder, nbdays=30):
    inflatedfolder = activefolder[:-1] + f"_{nbdays}days"
    if not exists(inflatedfolder):
        mkdir(inflatedfolder)
    vehicles = sorted(listdir(basefolder))
    for filename in sorted(listdir(activefolder)):
        with open(join(inflatedfolder, filename),"w") as f:
            for _ in range(nbdays):
                print(choice(vehicles), file=f)


## sizes functions

def nb_records(folder):
    return sum(len(load(join(folder,car))) for car in sorted(listdir(folder)))

def write_sizes(folder, outfilename):
    with open(outfilename, 'w') as outf:
        for car in sorted(listdir(folder)):
            print(os.path.getsize(join(folder,car)), file=outf)

def write_sizesv(folder, outfilename):
    with open(outfilename, 'w') as outf:
        for car in sorted(listdir(folder)):
            if 'gpx' in car:
                basename = join(folder,car)[:-7]
                print(sum(os.path.getsize(basename+ext) for ext in
                    ['gpx.txt', 'EngineSpeed.txt', 'EradAout_N_Actl.txt']
                    if exists(basename+ext)),
                    file=outf)
