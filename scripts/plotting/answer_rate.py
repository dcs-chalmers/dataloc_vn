#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 07:15:54 2019

@author: bhavers
"""

import os
import sys
sys.path.append("../..")
from sim import compare_internal_file_order
import numpy as np

def combinedLoadData(file1,file2,beijing=True):
    # compare file order, throw error if does not match!
    # see function documentation for more details
    if beijing:
        compare_internal_file_order([file1,file2])
        qs = []
        with open(file1,'r') as f1:
            with open(file2,'r') as f2:
                for line1, line2 in zip(f1,f2):
                    size = int(line2.split(",")[1])
                    q = [int(elem) for elem in line1.split(',')[1:-1]]
                    q.append(size)
                    qs.append(q)
    else: 
        qs = []
        with open(file1,'r') as f1:
            with open(file2,'r') as f2:
                for line1, line2 in zip(f1,f2):
                    size = int(line2)
                    q = [int(elem) for elem in line1.split(',')[0:-1]]
                    q.append(size)
                    qs.append(q)
    return qs



def listAdd(l1,l2):
    return [x1+x2 for x1,x2 in zip(l1,l2)]

def loadAll():
    all = []
    for f1,f2 in zip(qfiles,sizefiles):
        suball = combinedLoadData(f1,f2,beijing=False)
        all.extend(suball)
    return all


def binBySize(data,n):
    maximumSize = max([line[-1] for line in data])
    binWidth = maximumSize/n

    #print(f"max size: {maximumSize}")
    
    bins = [[0] * (len(data[0]))] * (n+1)
    for line in data:
        try:
            currentBin = int( line[-1] // binWidth ) 
            line = [1] + line
            bins[currentBin] = listAdd(bins[currentBin],line[:-1])
        except:
            print('overstepped:',currentBin)
        
    
    total = sum([line[0] for line in bins])
    
    for line in bins:
        if not line[0] == 0:
            line[1:] = [x/line[0] for x in line[1:]]
            line[0] /= total
    
    #print(f"bin width (in percentage): {binWidth}")
        
    return bins


def plot(data, n, filename):
    
    queries = [0,2,4,6,8]
    
    # ugly hardcording but lazy:
    binWidth = 923742.1818181818
    
    xvalues = [i * binWidth / ( 1024 * 1024 ) for i in range(n)][:15]
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    fig,ax1 = plt.subplots()
    ax2=ax1.twinx()
    
    ax1.plot(xvalues,[line[0] for line in data][:15])
    
    for i in queries:
        ax2.plot(xvalues,[line[i + 1] for line in data][:15],
                 linewidth=0.5,
                 label='q'+str(i + 1),
                 )
    
    ax1.set_xlabel('file size in MB')
    ax1.set_ylabel('distribution')
    ax2.set_ylabel('share of query answers')
    #plt.show()
    ax2.legend(
            ncol = len(queries),
            fancybox="off",
            edgecolor='black',
            facecolor='white',
            framealpha=1,
            loc=(-0.13,1.05))
    
    plt.savefig(filename,bbox_inches = 'tight',pad_inches = 0)
    
    
    

def plotbeijing():
    
    n = 33
    plot(binBySize(combinedLoadData('../../q.dat','../../size.dat'),n),n,"answers_rate_beijing.pdf")
    
    
def combinedPlot(n=33):
    
    data_beijing = binBySize(combinedLoadData('../experiments/q.dat','../experiments/size.dat'),n)
    
    xvalues = [100/n * i for i in range(n+1)]
    
    avg_answer_rate_beijing = [np.mean(line[1:]) for line in data_beijing]
    avg_answer_rate_beijing_upper = [np.mean(line[1:]) + np.std(line[1:]) for line in data_beijing]
    avg_answer_rate_beijing_lower = [np.mean(line[1:]) - np.std(line[1:]) for line in data_beijing]
    
    
    max_size_beijing = 1183023/(1024**2)

    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    fig,ax1 = plt.subplots()
    ax2=ax1.twinx()
    
    ax3=ax1.twiny()





    # ax1.plot(xvalues,[line[0] for line in data_beijing],
    #          color='blue',
    #          alpha=0.25,
    #          linewidth=1)
    ax1.fill_between(xvalues,[line[0] for line in data_beijing],
        facecolor="red",
        alpha=0.25,
        step="pre")
    
                 
    
    ax2.plot(xvalues,avg_answer_rate_beijing,
             color='red',
             linewidth=1)
    
    ax1.set_xlim([0,60])
    ax3.set_xlim([0,60])
    ax3.set_xticklabels([f"{np.round(i/100*max_size_beijing,1)}MB" for i in range(0,70,10)])

    ax1.set_ylabel('relative frequency')
    ax2.set_ylabel('average answer rate')
    


    from matplotlib.patches import Patch
    from matplotlib.legend_handler import HandlerLine2D, HandlerTuple

    p1 = Patch(facecolor="red", alpha=0.25)

    l1, = ax2.plot([1,1],color="red", linewidth=1)

    # m1, = ax2.plot([1,1],color="black", linestyle="None", marker="$/$", markersize=8)

    ax2.legend([(p1,l1)],[r'\textit{Geolife}'],
        handler_map={tuple: HandlerTuple(ndivide=None)},
        handlelength=3,
        # fancybox=False,
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        loc=(0.1,0.75))
    l1.set_visible(False)
    # m1.set_visible(False)

    
    ax3.set_xlabel(r'data volume (\textit{Geolife})')
    
    ax1.set_xticklabels([])
    

    plt.arrow(5.59,0.015,-4,0, head_width=0.005, head_length=0.8, color="black")
    plt.text(5.59+0.4,0.015,"shaded\nbars", va="center")


    plt.arrow(54,0.23, 4,0, head_width=0.005, head_length=0.8, color="black")
    plt.text(54-0.4,0.23,"solid lines", va="center", ha="right")

    ax1.set_ylim([0,0.25])
    ax2.set_ylim([0,0.6])

    plt.savefig("answers_rate_combined.pdf",bbox_inches = 'tight',pad_inches = 0.01)

    
    
combinedPlot()


