#!/usr/bin/env python3

from os import listdir, makedirs, remove, rename
from os.path import isdir, join, exists
from sys import argv
from time import process_time

from bisect import bisect_right as binsearch
from math import radians, sin, cos, atan2, sqrt
from itertools import chain
import kdtree

### Constants

b1, b2 = (40.1164, 116.1221), (39.7067, 116.6563)   # Beijing
c1, c2 = (39.95, 116.342), (39.8709, 116.4451)      # Inner City
d1, d2 = (39.933, 116.3675), (39.8992, 116.4196)    # Downtown

SEC, MINUTE, HOUR, DAY = 1, 60, 3600, 86400

### Load/Parse/Precompute

def load(filename):
    with open(filename, "r") as file:
        return [tuple(map(float,line.strip().split(",")))
                for line in file.readlines() if line.strip()]

def load_day(filename, day):
    with open(filename, "r") as file:
        data = []
        for line in file.readlines():
            record = list(map(float,line.split(",")))
            record[0] += day*DAY
            data.append(tuple(record))
        return data

def load_days(filename, basefolder):
    with open(filename, "r") as file:
        lines = file.readlines()
        return list(chain(*[load_day(join(basefolder, lines[i].rstrip('\n')), i)
                              for i in range(len(lines))]))

### Query over a folder

def apply_query(folder, Q, *args):
    return [Q(load(join(folder,file)),*args) for file in sorted(listdir(folder))]

def query(folder, Q, *args):
    files = sorted(listdir(folder))
    return sum(Q(load(join(folder,file)),*args) for file in files)/len(files)

def querydays(basefolder, daysfolder, Q, *args):
    files = sorted(listdir(daysfolder))
    return sum(Q(load_days(join(daysfolder,file), basefolder),*args)
               for file in files)/len(files)

def queryall(Q, filename, basefolder, mindays, load_function=load, *args):
    with open(filename, "r") as file:
        satisfyingdays = 0
        for line in file.readlines():
            if Q(load_function(join(basefolder,line[:-1])),*args):
                satisfyingdays += 1
            if satisfyingdays >= mindays:
                return True
        return False

def queryndays(basefolder, daysfolder, Q, mindays=1, loadf=load, *args):
    files = sorted(listdir(daysfolder))
    return sum(queryall(Q, join(daysfolder, file), basefolder, mindays,
                        loadf, *args) for file in files)/len(files)

### Kd-tree & Distance

def distance(lat1, lon1, lat2, lon2):
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = (sin(dlat/2) * sin(dlat/2) +
         cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2))
    return 6371000 * 2 * atan2(sqrt(a), sqrt(1 - a))

def dist_closest(lat,lon,kdtree):
    objlat, objlon = kdtree.search_nn((lat,lon))[0].data
    return distance(lat,lon,objlat,objlon)

def within_distance_kdtree(data, kdtree, maxdist):
    return any(dist_closest(rec[1],rec[2],kdtree) <= maxdist for rec in data)

def passed_closeby_nobjects(data, kdtree, maxdist, ntimes):
    passedby = set()
    for rec in data:
        t, lat, lon = rec[0], rec[1], rec[2]
        objlat, objlon = kdtree.search_nn((lat,lon))[0].data
        if ( (objlat, objlon) not in passedby and
             distance(lat,lon,objlat,objlon) <= maxdist ):
            passedby.add((objlat, objlon))
            if len(passedby) == ntimes:
                return True
    return False
     
def has_refilled_tank_old(data, kdtree, maxdist=50, delta=10, mintime=60):
    def close_points():
        for rec in data:
            t, lat, lon = rec[0], rec[1], rec[2]
            objlat, objlon = kdtree.search_nn((lat,lon))[0].data
            if distance(lat,lon,objlat,objlon) <= maxdist:
                yield t
    ts = t1 = None
    for t in close_points():
        if ts and (t-t1) <= delta:
            if (t-ts) >= mintime:
                return True 
        else:
            ts = t
        t1 = t
    return False

def stopped_close2object(data, objects, maxdist=10, duration=600, maxpseed=0):
    def stop(r1, r2):
        if instant_speed(r1, r2) <= maxpseed:
           objlat, objlon = objects.search_nn((r1[1],r1[2]))[0].data
           if distance(r1[1],r1[2],objlat,objlon) <= maxdist:
               return True
        return False
    for batch in continuous_batches(data, duration, stop):
        return True
    return False

def has_refilled_tank(data, kdtree, maxdist=15):
    return stopped_close2object(data, kdtree, maxdist, 300, 10)

## Query Templates

def binslice(data, t0, t1):
    return data[ binsearch(data, (t0,0,0)) : binsearch(data, (t1,0,0)) ]

def has_enough_data(data, t0=0, t1=DAY, nb_records=1):
    return len(binslice(data,t0,t1)) >= nb_records

def is_within(x, y, p1, p2):
    return p2[0] <= x <= p1[0] and p1[1] <= y <= p2[1]

def passed_by(data,p1,p2):
    return any(is_within(rec[1],rec[2],p1,p2) for rec in data)

def stayed_in(data,p1,p2):
    if not data:
        return False
    return all(is_within(rec[1],rec[2],p1,p2) for rec in data)

def allrec_outside_zone(data,p1,p2):
    if not data:
        return False
    return all(not is_within(rec[1],rec[2],p1,p2) for rec in data)

def space_filter(data, p1, p2):
    return [(rec[0],rec[1],rec[2]) for rec in data
            if is_within(rec[1],rec[2],p1,p2)]

def continuous(data, validator):
    i = 0
    while i < len(data):
        j = i
        while j < len(data)-1 and validator(data[j+1],data[j]):
            j += 1
        if data[i:j]:
            yield data[i:j]
        i = j+1

def continuous_batches(data, minspan, validator, t0=0, t1=DAY, nb_records=1):
    yield from (sub for sub in continuous(binslice(data,t0,t1), validator)
                if len(sub) >= nb_records and (sub[-1][0]-sub[0][0]) >= minspan)

def has_continuous_data(data, t0=0, t1=DAY, maxd=float("inf"), minspan=0, m=1):
    within_delay = lambda d1, d2 : abs(d1[0]-d2[0]) <= maxd
    for batch in continuous_batches(data,minspan,within_delay,t0,t1,m):
        return True
    return False

def instant_speed(rec1, rec2):
    if rec2[0] == rec1[0]:
        return 0
    return 3.6*distance(rec1[1],rec1[2],rec2[1],rec2[2]) / abs(rec2[0]-rec1[0])

def speed(data, delta=15):
    record1 = None
    for record2 in data:
        if record1 and abs(record2[0]-record1[0]) <= delta:
            yield instant_speed(record1, record2)
        record1 = record2

def stopped(data, duration=600, maxspeed=0):
    stop = lambda r1, r2: instant_speed(r1, r2) <= maxspeed
    for batch in continuous_batches(data, duration, stop):
        return True
    return False

def average_speed(data):
    speeds = [s for s in speed(data)]
    return sum(speeds)/len(speeds) if speeds else None


## Queries from the paper Q1 to Q10 -- Beijing dataset; loading included

delta_B = (80, 5)

def q1(data, t0=8*HOUR, t1=12*HOUR, m=1):
    return has_enough_data(data, t0, t1, m)

def q2(data, parkingsfile="parkings.csv", maxdist=50):
    parkingstree = kdtree.create(load(parkingsfile))
    return within_distance_kdtree(data, parkingstree, maxdist)

def q3(data, t0=17*HOUR, t1=18*HOUR, tau=delta_B[0], delta=delta_B[1], m=1):
    return has_continuous_data(data, t0, t1, delta, tau, m)

def q4(data, p1=c1, p2=c2):
    return passed_by(data, p1, p2)

def q5(data, maxspeed=89, t0=17*HOUR, t1=18*HOUR):
    return any(s >= maxspeed for s in speed(binslice(data,t0,t1))) 

def q6(data, minspeed=42, tau=10*MINUTE, delta=10):
    for b in continuous_batches(data, tau,
         lambda rec1, rec2 : instant_speed(rec1, rec2) >= minspeed
            and abs(rec2[0]-rec1[0]) <= delta):
        return True
    return False

def q7(data, p1=d1, p2=d2, tau=delta_B[0], delta=delta_B[1], t0=0, t1=DAY):
    return has_continuous_data(space_filter(data,p1,p2), t0, t1, delta, tau, 1)

def q8(data, p1=c1, p2=c2, t0=17*HOUR, t1=18*HOUR):
    return passed_by(binslice(data,t0,t1), p1, p2)

def q9(data, p1=c1, p2=c2):
    return stayed_in(binslice(data,12*HOUR,13*HOUR), p1, p2)

def q10(data, fuelsfile="fuels.csv", maxdist=50):
    fueltree = kdtree.create(load(fuelsfile))
    return has_refilled_tank_old(data, fueltree, maxdist)


## Generate "time.dat" and "q.dat" files ##

def generate_time_q_files(folder, queries, qntimes, outtime, outq):
    with open(outtime, 'w') as filetime:
        with open(outq, 'w') as fileresolution:
            for vehicle in sorted(listdir(folder)):
                print(vehicle, end=",", file=filetime)
                print(vehicle, end=",", file=fileresolution)
                for i in range(len(queries)):
                    qtime = 0
                    for _ in range(qntimes):
                        start = process_time()
                        res = queries[i](join(folder,vehicle))
                        qtime += 1000 * (process_time() - start)
                    print(round(qtime/qntimes,2), end=',', file=filetime)
                    print(int(res), end=',', file=fileresolution)
                print(file=filetime)
                print(file=fileresolution)

def short_queries(queries):
    return [(lambda qf: lambda file: qf(load(file)))(q) for q in queries]

## short queries generation ##

def gen_beijing_timeq_files(folder, timefilename='time.dat', qfilename='q.dat'):
    generate_time_q_files(folder,
                          short_queries([q1,q2,q3,q4,q5,q6,q7,q8,q9,q10]),
                          3, timefilename, qfilename)


## long queries generation ##

def long_queries(queries, nbdays, basefolder):
    return [(lambda qf, m: lambda file: queryall(qf, file, basefolder, m))
            (queries[i],nbdays[i]) for i in range(len(queries))]

def gen_beijing_longtimeq_files(folder, basefolder,
                                timefilename='longtime.dat',
                                qfilename='longq.dat'):
    generate_time_q_files(folder,
        long_queries([q1,q3,q4,q5,q6,q7,q8], [18,10,8,6,5,4,4], basefolder),
                          3, timefilename, qfilename)

