from os import listdir
from os.path import join, getsize
import sys
sys.path.append("../datasets/")


from paths import *

# Generate a "size" file: 1 line with the size in bytes of each vehicle's data
def size(datafolder,outputfilename="size.dat"):
    with open(outputfilename, "w") as outputfile:
        for filename in sorted(listdir(datafolder)):
            print(filename,getsize(join(datafolder,filename)), file=outputfile, sep=",")

# Generate "size.dat" -- replace by paths to preprocessed dataset.
size(beijing_folder)
