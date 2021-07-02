#!/usr/bin/env python3

from random import random, randint, shuffle
from math import ceil

from collections import defaultdict
from sortedcontainers import SortedList
from priority_dict import priority_dict

from query import *

from statistics import stdev

### Loading Function ###

def loadtime(filename):
    with open(filename) as f:
        return [list(map(float,line.split(',')[1:-1])) for line in f.readlines()]


def loadquery(filename):
    with open(filename) as f:
        return [list(map(int,line.split(',')[1:-1])) for line in f.readlines()]


def compare_internal_file_order(files: list):
    """
    This function will check whether the passed files are in the same order.
    This is done by comparing first the lengths of the files, and then the first
    element of each line of each file. This first element contains the filename
    corresponding to the vehicle that the data of this line belongs to.

    If a check fails, an assertion error is thrown.
    """

    def list_equal(somelist: list) -> bool:
        return all(somelist[0] == x for x in somelist)

    data = []
    for file in files:
        with open(file, "r") as f:
            data.append([line.split(",")[0] for line in f.readlines()])

    lengths = [len(datai) for datai in data]
    assert(list_equal(lengths)), f"input files {files} have different lengths: {lengths}."

    for i in range(len(data[0])):
        assert(list_equal([data[j][i] for j in range(len(data))])), f"mismatch found at line {i+1} in files {files}"


def loadsize(filename):
    with open(filename) as f:
        return [int(line) for line in f.readlines()]

### Main Simulator ###

def is_active(vehicle, time):
    return any(start <= time <= end for (start,end) in vehicle)


### EVENT-TYPES for the simulator ###

VEHICLE_JOINING = -2
TRIGGERED_TIMER = -1
LATE_ANSWER = 0
ONTIME_ANSWER = 1

    
def simulator(algorithm, vehicles, queries, custom_latency, workfunction, queryanswer,
              ending_time=None, timer_duration=1000, starting_time=0,
              verbose=False):
    """
    algorithm:          selects the set of cars to answer the queries
    
        algorithm.initpools(vehicles,queries): initialize the set of
                        contactable vehicles for each query
                        
        algorithm.firstbatch(q,n): set of vehicles to contact during the
                        first round for query (q,n)
                        
        algorithm.update(q,v,t,a,work,message_type):
                        update internal statistics after receiving an answer a
                        from vehicle v for query q at time t
                        message_type indicates if it was received after
                        the corresponding timer LATE_ANSWER vs ONTIME_ANSWER;
                        work is the amount of work used on the vehicle
                        
        algorithm.nextbatch(current_time, q, remaining_answers): next set of
                        vehicles to contact for query q at current_time

        algorithm.timer_triggered(time, q, v): function called upon a timer
                        get trigerred before the corresponding answer is
                        received (query q and vehicle v); otherwise, the timer
                        is just ignored.

        algorithm.new_active_vehicle(t, v): reaturn a list of (query,vehicle)
                        upon a vehicle v is becoming available
                        for query answering at time t.
                        
    vehicles:           list of "active periods" for each participating vehicles
                        eg [(t1,t2),(t3,t4), ...] where the vehicle is inactive
                        between (t2,t3), hence uncontactable and not answering
                        
    queries:            a list of queries (query_id, nb_answers, transfer_time)
                        to run on the fleet
    
    workfunction(q,v):  generate the amount of work for vehicle v and query q
    
    queryanswer(q,v):   generate the answer for vehicle v and query q

    custom_latency:     a single-trip latency for transferring messages. If this is
                        a function, it should return a latency in milliseconds if
                        custom_latency() is called. Will then be called once before
                        contacting each vehicle.
    
    starting_time:      clock time in s when the simulation is started, eg 18:00
                        [default 0]

    ending_time:        shorten the simulation by discarding vehicles joining
                        after that point in time
                        [default None, ie process all input data]
                        
    timer_duration:     fixed time duration (in ms)
                        for timers triggering actions to non-answers
                        [default 1 s]
                        
    verbose:            enable verbose mode
    """
    messages = SortedList()
    queue = [starting_time]*len(vehicles)
    works = [0]*len(vehicles)
    answers = [n for q,n,qt in queries]
    total_answers = sum(answers) 
    timequery = [0]*len(queries)
    noanwers = [0]*len(queries)
    estimation = [0]*len(queries)


    latency_is_func = False
    try:
        custom_latency()
        latency_is_func = True
    except:
        pass

    
    # for now, mono-task vehicles with fifo queue
    def execute_query_and_send_answer(time, q, v):
        
        latency = custom_latency() if latency_is_func else custom_latency

        ready = time + latency / 1000 + queries[q][2] / 1000
        # In any case set a timer for the vehicule
        timer = time + timer_duration / 1000
        if verbose:
            print(f"{round(time,4)};",
              f"timer set for query {q} and vehicle {v} to {round(timer,4)};")
            print(f"{round(time,4)};",
              f"latency: {latency} ms;")
        # is the vehicle active upon receiving the full query?
        for (start, end) in vehicles[v]:
            if start <= ready <= end: # query get stacked
                # work is accounted regardless of future status
                # now time is accounted in seconds
                work = workfunction(queries[q][0], v) / 1000
                works[v] += work
                queue[v] = max(queue[v] + work, ready + work)

                if queue[v] < end: # query answer sent back
                    
                    if verbose:
                        print(f"{round(time,4)};",
                              f"query {q} sent to <active> vehicle {v};")

                    # either late answer or answer before timer?
                    if queue[v] + latency / 1000 > timer:
                        messages.add((timer, q, v, -1))
                        messages.add((queue[v] + latency / 1000, q, v,
                                      LATE_ANSWER))
                        
                    # else timer is ignored as triggered after answer
                    else:
                        messages.add((queue[v] + latency / 1000, q, v,
                                      ONTIME_ANSWER))
                    
                else: # query aborted as vehicle is missing
                    if verbose:
                        print(f"{round(time,4)};",
                              f"query {q} sent to <active> vehicle {v};",
                              f"query aborted at {end};")
                    messages.add((timer, q, v, TRIGGERED_TIMER))
                
                break
        else: # vehicle v is inactive at query's execution time
            if verbose:
                print(f"{round(time,4)};",
                  f"sent query {q} to <inactive> vehicle {v};")
            messages.add((timer, q, v, TRIGGERED_TIMER))

    # uppon answer reception
    def receive_answer(time, q, v):
        nonlocal total_answers
        answer = queryanswer(queries[q][0], v)
        if verbose:
            print(f"{round(time,4)};",
                  f"answer received for {q} from {v}: {bool(answer)};",
                  f"remaining answers for {q}: {answers[q]-answer};")
        if answer:
            if answers[q] > 0:  # otherwise, the query is already resolved
                total_answers -= 1
            answers[q] -= 1
            if answers[q] == 0:
                timequery[q] = time
                n = queries[q][1]
                estimation[q] = round(n/(n+noanwers[q]), 5)
                if verbose:
                    print(f"{round(time,4)};", f"query {q} resolved;",
                      f"estimation of yes-answers for {q}: {estimation[q]};")
        else:
            noanwers[q] += 1

    # Initialization of the random query order
    shuffled_queries = list(range(len(queries)))
    shuffle(shuffled_queries)

    # Initialization of the vehicle pools; assumption: the initial pool is made
    # of the active vehicles at queries' starting time
    vpool = [v for v in range(len(vehicles))
             if is_active(vehicles[v],starting_time)]
    if verbose:
        print(f"Start: {starting_time}; {len(vpool)} active vehicles;")
    algorithm.initpools(vpool, queries)

    # Prepare future vehicles' joining
    for v in range(len(vehicles)):
        for start, end in vehicles[v]:
            if (start > starting_time and
                (not ending_time or start <= ending_time)):
                messages.add((start, -1, v, VEHICLE_JOINING))

    # Initial Batch
    for q in shuffled_queries:
        if verbose:
            print(f"Initialization of query {q};")
        # send all queries simultaneousely at "starting time"
        for v in algorithm.firstbatch(q, queries[q][1]): 
            execute_query_and_send_answer(starting_time, q, v) 

    # Main message loop
    while messages:
        time, q, v, message_type = messages.pop(0)

        if ending_time and time > ending_time: # stop the simulation
            break

        if message_type is VEHICLE_JOINING:
            for q,vp in algorithm.new_active_vehicle(time, v):
                if verbose:
                    print(f"{round(time,12)};",
                          f"vehicle {v} becomes active;",
                          f"query {q} sent to {vp};")
                execute_query_and_send_answer(time, q, vp)
            continue
        
        if message_type is LATE_ANSWER or message_type is ONTIME_ANSWER:
            receive_answer(time, q, v)
            qv = [queries[q][0], v]
            algorithm.update(q, v, time, queryanswer(*qv), workfunction(*qv),
                             message_type)

        elif message_type is TRIGGERED_TIMER:
            if verbose and total_answers > 0:
                print(f"{round(time,4)};",
                          f"timer for query {q} vehicle {v} triggered;")
            algorithm.timer_triggered(time, q, v)

        for vp in algorithm.nextbatch(time, q, answers[q]):
            execute_query_and_send_answer(time, q, vp)
        

    # Unresolved queries' resolution times are set to 'inf' time
    for q in shuffled_queries:
        if answers[q] > 0:
            timequery[q] = float('inf')
            yes_answers = queries[q][1]-answers[q]
            if yes_answers+noanwers[q] > 0:
                estimation[q] = round(yes_answers/(yes_answers+noanwers[q]), 5)
            if verbose:
                print(f"query {q} aborted un-resolved;",
                      f"estimation of yes-answers for {q}: {estimation[q]};")

    # Output Datastructure
    # list of exec time for q_i,
    # total workload,
    # list of queries' number of received answers at queries resolution
    # list of queries' number of received answers at algorithm's end
    # list of estimation of answer rate for q_i upon queries' completion
    # list of local work
    return ([round(1000*(t-starting_time),2) for t in timequery],
            round(1000*sum(works),2),
            estimation,
            [round(w,2) for w in works])

    
### Algorithms ###
class QuerySpreadingAlgorithm:
    def initpools(self, vehicles, queries):
        self.queries = range(len(queries))
        
        self.pools = [vehicles[:] for _ in queries]
        for pool in self.pools:
            shuffle(pool)

        self.querried_vehicles = [set() for _ in range(len(queries))]
        self.remaining_answers = [n for q,n,qt in queries]
        self.no_queried_vehicles = [0]*len(queries)
    
    def firstbatch(self, query, n):
        pq = self.pools[query]
        return [pq.pop() for _ in range(min(n,len(pq)))]

    def update(self, query, vehicle, time, answer, work, msg_type):
        self.querried_vehicles[query].add(vehicle)
        self.remaining_answers[query] -= 1 if answer else 0

    def nextbatch(self, time, query, remaining_answers):
        return []

    def timer_triggered(self, time, query, vehicle):
        pass

    def new_active_vehicle(self, time, vehicle):
        return []
    
# "fast algorithm" -- ignoring timers / late answers
class Baseline1(QuerySpreadingAlgorithm):
    def firstbatch(self, query, n):
        return self.pools[query]

    def new_active_vehicle(self, time, vehicle):
        return [(q,vehicle) for q in self.queries
                if self.remaining_answers[q] > 0]

# "slow algorithm" -- all timers considered negative
class Baseline2(QuerySpreadingAlgorithm):
    def initpools(self, vehicles, queries):
        super().initpools(vehicles, queries)
        
    def firstbatch(self, query, n):
        batch = super().firstbatch(query, n)
        self.no_queried_vehicles[query] += len(batch)
        return batch
        
    def update(self, query, vehicle, time, answer, work, msg_type):
        super().update(query, vehicle, time, answer, work, msg_type)
        if msg_type is ONTIME_ANSWER:
            self.no_queried_vehicles[query] -= 1
        self.one_more_vehicle = ((not answer) and (msg_type is ONTIME_ANSWER))
    
    def timer_triggered(self, time, query, vehicle):
        self.one_more_vehicle = True
        self.no_queried_vehicles[query] -= 1

    def new_active_vehicle(self, time, vehicle):
        to_query = []
        for query in self.queries:
            if vehicle not in self.querried_vehicles[query]:
                if (self.remaining_answers[query] > 0 and
                    self.no_queried_vehicles[query] == 0):
                    self.no_queried_vehicles[query] += 1
                    to_query.append((query,vehicle))
                self.pools[query].append(vehicle)
        return to_query
    
    def nextbatch(self, time, query, remaining_answers):
        if self.remaining_answers[query] > 0 and self.one_more_vehicle and self.pools[query]:
            self.no_queried_vehicles[query] += 1
            return [self.pools[query].pop()]
        return []

# sends a new query uppon any response
class Baseline2Variant(QuerySpreadingAlgorithm):
    def nextbatch(self, time, query, remaining_answers):
        if remaining_answers > 0 and self.pools[query]:
            return [self.pools[query].pop()]
        return []

# "good algorithm"
class BalancedAlgo(QuerySpreadingAlgorithm):
    def __init__(self, alpha=1.25, beta=0.7):
        self.alpha = alpha
        self.beta = beta

    def initpools(self, vehicles, queries):
        super().initpools(vehicles, queries)
        self.nb_received_answers = [0]*len(queries)
        self.nb_positive_answers = [0]*len(queries)
        self.querried_vehicles = [set() for _ in range(len(queries))]
        self.remaining_answers = [n for q,n,qt in queries]
        self.k = len(vehicles)
        self.querried = [0]*len(queries)

    def firstbatch(self, query, n):
        batch = super().firstbatch(query, n)
        self.querried[query] += len(batch)
        return batch

    def update(self, query, vehicle, time, answer, work, msg_type):
        self.querried_vehicles[query].add(vehicle)
        self.remaining_answers[query] -= 1 if answer else 0
        self.nb_received_answers[query] += 1 if msg_type is ONTIME_ANSWER else 0
        self.nb_positive_answers[query] += 1 if answer else 0

    def timer_triggered(self, time, query, vehicle):
        self.nb_received_answers[query] += 1
        pass
        
    def new_active_vehicle(self, time, vehicle):
        for query in self.queries:
            if (vehicle not in self.querried_vehicles[query] and
            self.remaining_answers[query] > 0):
                self.pools[query].append(vehicle)
        
        next_batch = [(query, vehicle) for query in self.queries for vehicle in
                self.nextbatch(time,query,self.remaining_answers[query])]
        self.querried[query] += len(next_batch)
        return next_batch

    def _pick_new_car(self, query):
        return self.pools[query].pop()

    def nextbatch(self, time, query, remaining_answers):
        queried = self.querried[query]
        received = self.nb_received_answers[query]
        
        if (self.remaining_answers[query] > 0 and self.pools[query]
            and received/queried >= self.beta):
            
            positives = self.nb_positive_answers[query]
            futures = queried - received

            p = max(positives/received, 1/(received+1))
            r = ceil(self.alpha * round(remaining_answers-futures*p) / p)

            next_batch = [self._pick_new_car(query)
                    for _ in range(min(r,len(self.pools[query])))]
            self.querried[query] += len(next_batch)
            return next_batch
        
        return []

# "fairer algorithm"
class FairAlgo(BalancedAlgo):
    def initpools(self, vehicles, queries):
        self.pools = [priority_dict() for q in queries]
        self.nb_received_answers = [0]*len(queries)
        self.nb_positive_answers = [0]*len(queries)
        self.k = len(vehicles)
        self.queries = range(len(queries))
        self.querried_vehicles = [set() for _ in self.queries]
        self.remaining_answers = [n for q,n,qt in queries]
        self.querried = [0]*len(queries)
        
        for v in vehicles:
            for q in range(len(self.queries)):
                self.pools[q][v] = (0,0,random())

    def _update_nbquery(self, vehicle, update):
        for q in self.queries:
            if vehicle in self.pools[q]:
                nbq, vtime, r = self.pools[q][vehicle]
                self.pools[q][vehicle] = (nbq+update, vtime, r)
    
    def _update_vtime(self, vehicle, work):
        for q in self.queries:
            if vehicle in self.pools[q]:
                nbq, passedwork, r = self.pools[q][vehicle]
                self.pools[q][vehicle] = (nbq, passedwork+work, r)

    """ Pick car that (1) "do not compute now" if possible
                      (2) have not worked much so far
        Order by (# of queries running on it, time spent so far, Random"""
    def _pick_new_car(self, query):
        vehicle = self.pools[query].pop_smallest()
        self._update_nbquery(vehicle, +1)
        return vehicle

    def firstbatch(self, query, n):
        next_batch = [self._pick_new_car(query) for _ in range(n)]
        self.querried[query] += len(next_batch)
        return next_batch

    def update(self, query, vehicle, time, answer, work, msg_type):
        self.nb_received_answers[query] += 1
        self.nb_positive_answers[query] += 1 if answer else 0
        self._update_nbquery(vehicle, -1)
        self._update_vtime(vehicle, work)
        self.remaining_answers[query] -= 1 if answer else 0
        self.querried_vehicles[query].add(vehicle)

    def new_active_vehicle(self, time, vehicle):
        for query in self.queries:
            if (vehicle not in self.querried_vehicles[query] and
            self.remaining_answers[query] > 0):
                self.pools[query][vehicle] = (0,0,random())
        
        return [(query, vehicle) for query in self.queries for vehicle in
                self.nextbatch(time,query,self.remaining_answers[query])]


### Experiment Utils ###

### Tested Algorithms -- Static Model First ###

### DATASETS: Beijing Shortcuts
#delay_4g = 50, speed_4g = 1 # in KB/ms; average latency 4G 50ms
#delay_5g = 5, querysize_5g = [0]*15; average latency 5G 10ms (expected)

## Static Model: Fake Full Day Single Active Period (0,86400) ##
def parameters(queries, latency, time_file, answer_file):
    times, query = loadtime(time_file), loadquery(answer_file)
    compare_internal_file_order([time_file,answer_file])        # check if files are in correct order
    return  [[[(0,86400)]]*len(times),                          # vehicles
            queries,                                            # queries
            latency,                                            # latency
            lambda q, v : times[v][q],                          # work function
            lambda q, v : query[v][q]]                          # query answer

### Beijing Dataset -- 50 answers for 10 queries
qsizesbeijing = [0.3, 7.5, 1.3, 0.5, 1.1, 1.6, 1.4, 0.8, 0.7, 3.8]

def simbeijing(algo, queries=None, tfile='time.dat', qfile='q.dat', latency=50,
               starting_time=0, verbose=False):
    queries = queries if queries else [(q,50) for q in range(10)]
    qnsize = [(q,n,qsizesbeijing[q]) for (q,n) in queries]
    return simulator(algo, *parameters(qnsize, latency, tfile, qfile),
                     starting_time=starting_time, verbose=verbose)[:2]



### Experiments ###

def average_resolution_time(algo, m=1000):
    """ plot the average time needed by each query to get resolved and at last
    the average resolution time and total work needed to resolve all queries """
    queries, total = algo()
    resolution_time = max(queries)
    for _ in range(m-1):
        times, total_ = algo()
        for i in range(len(queries)):
            queries[i] += times[i]
        resolution_time += max(times)
        total += total_
    for i in range(len(queries)):
        print(i, round(queries[i]/m,2))
    print(round(resolution_time/m,2), round(total/m,2))

def repeat_simulation(algo, outfilename, m=1000):
    """ repeat m simulations and write query resolution times to outfilename """
    with open(outfilename,'w') as f:
        queries, total = algo()
        for _ in range(m-1):
            times, total_ = algo()
            for i in range(len(queries)):
                queries[i] += times[i]
                print(round(times[i],2), end=',', file=f)
            total += total_
            print(round(total_,2), file=f)
        for i in range(len(queries)):
            print(round(queries[i]/m,2), end=',', file=f)
        print(round(total/m,2), file=f)


### Choice of "n" for experiments -- Run 5 simultaneous queries ###

def simnbeijing(algo, n, tfile='time.dat', qfile='q.dat', latency=50):
    qnsize = [(q,n,qsizesbeijing[q]) for q in [0,1,2,3,4]]
    return simulator(algo, *parameters(qnsize, latency, tfile, qfile))[2]


qbeijing = [0.566175, 0.434645, 0.283344, 0.191457, 0.117087]
       
def repeat_estimation_simulation(nb_simulations=1, outfilename="error.csv",
                                 simfunction=simnbeijing, qbase=qbeijing):
    algos = [Baseline1(), Baseline2(), BalancedAlgo(), FairAlgo()]
    with open(outfilename, "w") as f:
        for _ in range(nb_simulations):
            for i in range(len(algos)):
                for n in [10,25,50,75,100,125,150,175]:
                    print(i, n, end=',', sep=',', file=f)
                    qestimates = simfunction(algos[i],n)
                    for (q, qest) in zip(qbase, qestimates):
                        error = abs(q-qest)
                        print(round(error,4), end=',', file=f)
                    print(file=f, flush=True)

### Fairness of the algorithms ###

def simfairnessbeijing(algo, tfile='time.dat', qfile='q.dat', latency=50):
    qnsize = [(q,50,qsizesbeijing[q]) for q in range(10)]
    return simulator(algo, *parameters(qnsize, latency, tfile, qfile))[3]


def write_works(filename="works.csv", simfunction=simfairnessbeijing):
    with open(filename, "w") as f:
        algos = [Baseline1(), Baseline2(), BalancedAlgo(), FairAlgo()]
        works = [simfunction(algo) for algo in algos]
        for i in range(len(works[0])):
            print(*[works[k][i] for k in range(4)], sep=',', file=f, flush=True)

def fairness_measure(works):
    return 1-2*stdev(works)/31476.4

def repeat_fairness_simulation(nb_simulations=1, outfilename="fairness.csv",
                                 simfunction=simfairnessbeijing):
    algos = [Baseline2(), BalancedAlgo(), FairAlgo()]
    with open(outfilename, "w") as f:
        for _ in range(nb_simulations):
            works = [simfunction(algo) for algo in algos]
            print(*[stdev(work) for work in works], sep=',', file=f, flush=True)

def fairness_simulation_baseline1(outfilename="fairness_baseline1.csv",
                                    simfunction=simfairnessbeijing):
    with open(outfilename, "w") as f:
        work = simfunction(Baseline1())
        print(stdev(work), file=f, flush=True)
    



### Dynamic Model ###

def load_active_periods(activefile):
    return [list(zip(v[::2],v[1::2])) for v in loadtime(activefile)]

def parameters_dynamic(queries, latency,
                       vehicle_file, time_file, answer_file,
                        scale_time=1):
    times, query = loadtime(time_file), loadquery(answer_file)
    # check if files are in correct order
    compare_internal_file_order([time_file,answer_file,vehicle_file])
    return  [load_active_periods(vehicle_file),                 # vehicles
            queries,                                            # queries
            latency,                                            # latency
            lambda q, v : scale_time*times[v][q],               # work function
            lambda q, v : query[v][q]]                          # query answer

def simulate_dynamic_beijing(algo, queries=None, 
                scale_time=1, scale_query=1, timer_duration=100,
                starting_time=0, ending_time=None,
                verbose=False):
    queries = queries if queries else [(q,50) for q in range(10)]
    #qsizesbeijinglong
    qnsize = [(q,n,qsizesbeijing[q]*scale_query) for (q,n) in queries]
    return simulator(algo,
                     *parameters_dynamic(qnsize, 50,
                                      "vehicles.dat", "time.dat", "q.dat",
                                      scale_time),
                     timer_duration=timer_duration*scale_time,
                     starting_time=starting_time, ending_time=ending_time,
                     verbose=verbose)[:2]


#eg
#simulate_dynamic_beijing(Baseline2(), [(q,50) for q in range(8)], starting_time=18*3600, ending_time=18.5*3600, scale_time=1000)

def simbeijing_dynamic(algo, outfilename, nb_simulations=1):
    with open(outfilename, "w") as f:
        for _ in range(nb_simulations):
            qtime, workload = simulate_dynamic_beijing(algo,
                            [(q,50) for q in range(7)],
                            scale_time=1000, scale_query=1000,
                            timer_duration=100, starting_time=18*3600,
                            ending_time=20*3600, verbose=False)
            print(*[q/1000 for q in qtime], workload/1000, sep=',',
              flush=True, file=f)