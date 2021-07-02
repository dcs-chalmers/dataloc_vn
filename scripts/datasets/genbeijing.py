#!/usr/bin/env python

from os import listdir, mkdir, remove
from os.path import isdir, join, exists
from sys import argv
from shutil import copy



from datetime import datetime, timedelta
from bisect import bisect_right as binsearch

### Generate day csv files from the original Geolife traces ###
# Geolife version 1.3, 182 users, 18670 traces, 69 label files
# 11152 unique date files in beijing time (10528 beijing area, 10610 w/o dupes)
# 3297 labeled date files (3182 beijing area; 169 taxi files, 3118 w/o dupes)
# 1603 vehicular-labeled date files (1521 beijing area, 1490 w/o dupes)
# 55 longest vehicular user trace date file (55 beijing area, 50 w/o dupes)

# Remove records outside a large region around Beijing -- 10528 day files, 726.8 MiB uncompressed
def is_beijing_area(lat, long):
    return 35 < lat < 45 and 105 < long < 130

# Only keep records around Beijing metropolitan area -- 10300 day files
def is_beijing_city(lat, long):
    return 39.7067 <= lat <= 40.1164 and 116.1221 <= long <=  116.6563

vehicular_label = lambda label: label in ["bus","car","taxi"]
todatetime = lambda s1, s2, f: (datetime.strptime(s1+" "+s2, f)+timedelta(hours=8))
label2datetime = lambda s1, s2: todatetime(s1,s2,"%Y/%m/%d %H:%M:%S")
record2datetime = lambda s1, s2: todatetime(s1,s2,"%Y-%m-%d %H:%M:%S")

def stream_records_beijing(file):
    with open(file, 'r') as f:
        for i in range(6):
            f.readline()
        t = None
        for line in f.readlines():
            rec = line.strip().split(",")
            
            lat, long = float(rec[0]), float(rec[1])
            alt = 0.3048*float(rec[3]) if rec[3] != -777 else 0
            if is_beijing_area(lat, long):
                dt = datetime.strptime(rec[5]+" "+rec[6], "%Y-%m-%d %H:%M:%S")
                beijingtime = dt+timedelta(hours=8)

                if t and beijingtime <= t: # suppress dupplicate records
                    continue
                
                t = beijingtime
                yield (beijingtime, lat, long, alt)
                

def generate_dataset_beijing(directory, outdir):
    if not isdir(outdir):
        mkdir(outdir)

    for user in sorted(listdir(directory)):
        udir = join(directory,user)
        labelfile = join(udir,"labels.txt")
        
        trajectories = join(udir,"Trajectory")

        created_files = set()   # used to track created files (in case the directory is not empty)

        for file in sorted(listdir(trajectories)):
            outdate = None
            
            for record in stream_records_beijing(join(trajectories,file)):
                if outdate is None or record[0].date() != outdate:
                    if outdate is not None:
                        outfile.close()
                    outdate = record[0].date()
                    outfilename = user+"."+str(outdate)+".csv"
                    if outfilename in created_files:
                        outfile = open(join(outdir,outfilename), "a")
                    else:
                        outfile = open(join(outdir,outfilename), "w")
                        created_files.add(outfilename)
                time_ = record[0].time()
                h, m, s = time_.hour, time_.minute, time_.second
                timestamp = h*3600+m*60+s
                outfile.write("{},{},{},{:.4f}\n".format(str(timestamp),
                               str(record[1]),str(record[2]),record[3]))
            outfile.close()



def stream_records_labels(file, labeldates, labels):
    with open(file, 'r') as f:
        for i in range(6):
            f.readline()
        for line in f.readlines():
            rec = line.strip().split(",")
            lat, long, alt = float(rec[0]), float(rec[1]), 0.3048*float(rec[3])
            if is_beijing_area(lat, long):
                dt = datetime.strptime(rec[5]+" "+rec[6], "%Y-%m-%d %H:%M:%S")
                beijingtime = dt+timedelta(hours=8)
                if not labeldates:
                    break
                if (labeldates[0] <= beijingtime <= labeldates[1] and
                    vehicular_label(labels[0])):
                    yield (beijingtime, lat, long, alt, labels[0])
                elif beijingtime > labeldates[0]:
                    del labeldates[0]
                    del labeldates[0]
                    del labels[0]

    
def generate_dataset_beijing_labels(directory, outdir):

    print("Starting creating the dataset...",end="")

    for user in sorted(listdir(directory)):

        udir = join(directory,user)
        labelfile = join(udir,"labels.txt")
        
        trajectories = join(udir,"Trajectory")

        labels = []
        labeldates = []

        best = 0
        bestfilename = None
        
        if exists(labelfile):
            with open(labelfile, "r") as f:
                f.readline()
                for line in f.readlines():
                    record = line.split()
                    labels.append(record[4])
                    startdate = label2datetime(record[0],record[1])
                    labeldates.append(startdate)
                    enddate = label2datetime(record[2],record[3])
                    enddate += timedelta(seconds=1)
                    labeldates.append(enddate)
            labeldates.sort()
            # odd index --> out, even index --> in
            #print(binsearch(labeldates,datetime(2007,6,26,19,32,28)))
            
            for file in sorted(listdir(trajectories)):
                outdate = outfile = None

                for record in stream_records_labels(join(trajectories,file),labeldates,labels):
                    if outdate is None or record[0].date() != outdate:
                        
                        
                        if outfile is not None and not outfile.closed:
                            outfile.close()
                            
                            if nbline > best:
                                best=nbline
                                bestfilename=outfilename

                        outdate = record[0].date()
                        outfilename = user+"."+str(outdate)+".csv"
                            
                        outfile = open(join(outdir,outfilename), "a")
                        nbline = 0
                        
                    time_ = record[0].time()
                    h, m, s = time_.hour, time_.minute, time_.second
                    timestamp = h*3600+m*60+s
                    nbline += 1
                    outfile.write("{},{},{},{:.4f}\n".format(str(timestamp),
                                   str(record[1]),str(record[2]),record[3]))

                
                if outfile is not None:
                    outfile.close()
                    if nbline > best:
                        best=nbline
                        bestfilename=outfilename

            
        if bestfilename:
            copy(join(outdir,bestfilename),join("beijing-best",bestfilename))

      
    print("\tDone.")
    


if __name__ == "__main__":


    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("geolife_dir", type=str, help=f"Directory containing the unzipped GeoLife 1.3 folder")

    args = parser.parse_args()

    outdir = "../../datasets/beijing"
    generate_dataset_beijing(join(args.geolife_dir, "Data"), outdir)
