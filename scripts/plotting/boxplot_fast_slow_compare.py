#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:33:51 2019

@author: bhavers
"""


import numpy as np
from violinify import violinify as violinify


def signif(x, p):
    x = np.asarray(x)
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags



files_names = ['sim_beijing_short_baseline1_alpha=1.25_beta=0.7', 'sim_beijing_short_baseline2_alpha=1.25_beta=0.7','sim_beijing_short_balanced_alpha=1.25_beta=0.7','sim_beijing_short_fair_alpha=1.25_beta=0.7']
files = ['../experiments/alpha=1.25_beta=0.7_beijing_all_algos_shortqueries/' + f for f in files_names]


files_churn= ["../experiments/alpha=1.25_beta=0.7_beijing_all_algos_dynamic/sim_beijing_dynamic_baseline1_alpha=1.25_beta=0.7",
        "../experiments/alpha=1.25_beta=0.7_beijing_all_algos_dynamic/sim_beijing_dynamic_baseline2_alpha=1.25_beta=0.7",
        "../experiments/alpha=1.25_beta=0.7_beijing_all_algos_dynamic/sim_beijing_dynamic_balanced_alpha=1.25_beta=0.7",
        "../experiments/alpha=1.25_beta=0.7_beijing_all_algos_dynamic/sim_beijing_dynamic_fair_alpha=1.25_beta=0.7"]


def loaddata(filename):
    data = np.loadtxt(filename,delimiter=",")
    return data[:-1] # cut off last line, which contained summaries


def loaddata_churn(filename):
    with open(filename,"r") as f:
        first_line = f.readline()
        axes = len(first_line.split(",")) - 1
        data = [[] for _ in range(axes)]
        successes_fails = [[0,0] for _ in range(axes)]

        for (ax,work_str) in zip(range(axes), first_line.split(",")[:-1]):
            if work_str == "inf":
                successes_fails[ax][1] += 1
            else: 
                successes_fails[ax][0] += 1
                work = float(work_str)
                data[ax].append(work)

        for line in f:
            for (ax,work_str) in zip(range(axes), line.split(",")[:-1]):
                if work_str == "inf":
                    successes_fails[ax][1] += 1
                else: 
                    successes_fails[ax][0] += 1
                    work = float(work_str)
                    data[ax].append(work)
    return data, [success/(success+fail) for success,fail in successes_fails]



def rowAverages(data,columns):
#    return [line[columns] for line in data]
    return [np.mean(line[columns]) for line in data]


def plot():
    
    colors = ["red","blue","green","black"]
    
    ghostlines = []
    
    
    fastgroup = [0]
    slowgroup = [5]
    
    
    basepos = 1
    largeoffset = 1.5
    smalloffset = 0.2
    width = 0.15

    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    
    ax1 = plt.subplot2grid((1,3),(0,0),colspan=2)
    
    for i in range(4):
        data = loaddata(files[i])
        ax1.boxplot([np.log10(rowAverages(data,fastgroup)),np.log10(rowAverages(data,slowgroup))],
                    positions = [basepos + i*smalloffset, basepos + largeoffset + i * smalloffset],
                    showfliers=False,
                    medianprops=dict(color=colors[i]),
                    boxprops=dict(color=colors[i]),
                    whiskerprops=dict(color=colors[i]),
                    capprops=dict(color=colors[i]),
                    widths=width)
        ghostline, = plt.plot([1,1],color=colors[i])
        ghostlines.append(ghostline)
    ax1.legend((ghostlines[0], ghostlines[1], ghostlines[2], ghostlines[3]),('algo1', 'algo2', 'algo3', 'algo4'),
        fancybox=True,
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        ncol = 4,
        loc=(-0.10,1.05))
    for i in range(4):
        ghostlines[i].set_visible(False)
    
    ax1.set_xlim([0.5,2+largeoffset])
    ax1.set_xticks([1+1.5*smalloffset,1+largeoffset+1.5*smalloffset])
    ax1.set_xticklabels(["fast group", "slow group"])
    
    ax1.set_yticks(np.arange(2, 6))
    ax1.set_yticklabels(10.0**np.arange(2, 6))
    ax1.set_ylim([2,5.7])

    ax1.set_ylabel("time")
    
    
    # ---------------------------------------------------------------------------
    
    ax2 = plt.subplot2grid((1,3),(0,2),colspan=1)
    
    for i in range(4):
        data = loaddata(files[i])
        ax2.boxplot([np.log10(rowAverages(data,[-1]))],
                    positions = [basepos + i*smalloffset],
                    showfliers=False,
                    medianprops=dict(color=colors[i]),
                    boxprops=dict(color=colors[i]),
                    whiskerprops=dict(color=colors[i]),
                    capprops=dict(color=colors[i]),
                    widths=width)
    
    length = 0.5
    
    #set labels on y-axis!!! logarithmic!
    
    ax2.set_xlim([1+1.5*smalloffset-length,1+1.5*smalloffset+length])
    ax2.set_xticks([1+1.5*smalloffset])
    ax2.yaxis.tick_right()
    ax2.set_ylabel("total work")
    ax2.yaxis.set_label_position("right")
    
    plt.show()
    
    
#plot()

def remove_numpy_nans(array_in):
    return [x for x in array_in if x != np.inf]
    



def altPlot():
    
    colors=['red','green','blue','black']
    
    
    baseline_time = loaddata(files[0])
    baseline_time_avg = 1 
    
    data_algo = []
    
    for i in range(0,4):
        data_algo.append(loaddata(files[i]))
        
    bp_algo = []
    for i in range(0,4):
        bpdata = [np.mean([x/baseline_time_avg for x in line[:-1]]) for 
                  line in data_algo[i]]
        bp_algo.append(bpdata)
        
  
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    
    
    ax1 = plt.subplot2grid((1,2),(0,0),colspan=1)
    

    

 
    violinify(ax1,[bp_algo[0],bp_algo[1],bp_algo[2],bp_algo[3]],
                positions = [1-1/5,2-1/5,3-1/5,4-1/5],
                widths=0.35,
                color='red',
                labeled_median=True,
                labels_median=[r"$\times$" + str(signif(np.median(bp_algo[i])/np.median(bp_algo[0]),2))
                                     if i>-1 else "" for i in range(4)])
    
  
    
    
    
    ax1.set_ylabel('query resolution time [ms]')

    ax1.set_xticks([1,2,3,4])
    
    ax1.set_xticklabels([r'\textsc{BaseEager}$^*$',r'\textsc{BaseLazy}',r'\textsc{BalReq}',
                         r'\textsc{BalLoad}'],
                        rotation=-45,
                        ha="left", rotation_mode="anchor")


    ax1.set_ylim([1*1e2, 1.3*1e5])
    ax1.tick_params(axis='x', which='major', pad=1)

    for i in range(3):
        ax1.plot([i+1.5,i+1.5],[ax1.get_ylim()[0],ax1.get_ylim()[1]],linestyle='--',color='gray',linewidth=1)
    

    ax1.set_xlim([0.5,4.5])
    ax1.set_yscale('log')
    # ax1.set_ylim([0.40,120])
    
    
    ax2 = plt.subplot2grid((1,2),(0,1),colspan=1)
    
    
    baseline_work = loaddata(files[1])
    baseline_work_avg = 1 #np.mean(baseline_work[:,-1])
    bp_algo2 = []
    
    for i in range(0,4):
        bpdata2 = [x/baseline_work_avg for x in data_algo[i][:,-1]]
        bp_algo2.append(bpdata2)
        
  

    violinify(ax2, [bp_algo2[0],bp_algo2[1],bp_algo2[2],bp_algo2[3]],
                positions = [1-1/5,2-1/5,3-1/5,4-1/5],
                widths=0.35,
                color='red',
                labeled_median=True,
                labels_median=[r"$\times$" + str(signif(np.median(bp_algo2[i])/np.median(bp_algo2[1]),2))
                                     if i!=-1 else "" for i in range(4)])
    
 


    from matplotlib.patches import Patch

    p1 = Patch(facecolor="red", alpha=0.25)

    l1, = ax2.plot([1,1],color="red", linewidth=1)
    ax2.legend([(p1,l1)],[r'\textit{Geolife}'],
        handlelength=1.1,
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        loc=(0.237,0.265))
    l1.set_visible(False)


    
    ax2.yaxis.tick_right()
    ax2.set_ylabel("fleet workload [ms]")
    ax2.yaxis.set_label_position("right")
    
    ax2.set_xticks([1,2,3,4])   
    ax2.set_xticklabels([r'\textsc{BaseEager}',r'\textsc{BaseLazy}$^*$',r'\textsc{BalReq}',
                     r'\textsc{BalLoad}'],
                    rotation=-45,
                    ha="left", rotation_mode="anchor")
    ax2.set_ylim([0.6*1e5,4.5*1e7])

    ax2.tick_params(axis='x', which='major', pad=1)

    for i in range(3):
        ax2.plot([i+1.5,i+1.5],[ax2.get_ylim()[0],ax2.get_ylim()[1]],linestyle='--',color='gray',linewidth=1)
    
    ax2.set_xlim([0.5,4.5])
    ax2.set_yscale('log')


    plt.subplots_adjust(wspace=0.05)
    
    plt.savefig('comparison_algorithms.pdf',bbox_inches = 'tight',pad_inches = 0.006)


def remove_numpy_nans(array_in):
    return [x for x in array_in if x != np.inf]


def altPlot_churn():
    
    colors=['red','green','blue','black']
    
    
    baseline_time = loaddata(files_churn[0])
    baseline_time_avg = 1 #np.mean(baseline_time[:,:-1])
    
    data_algo = []
    
    for i in range(0,4):
        data_algo.append(loaddata(files_churn[i]))
        
    bp_algo = []
    for i in range(0,4):
        bpdata = [np.mean([x/baseline_time_avg for x in line[:-1]]) for 
                  line in data_algo[i]]
        bp_algo.append(bpdata)
        
 

    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    
    
    ax1 = plt.subplot2grid((1,2),(0,0),colspan=1)
    

    
  
 
    violinify(ax1,[bp_algo[0],bp_algo[1],bp_algo[2],bp_algo[3]],
                positions = [1-1/5,2-1/5,3-1/5,4-1/5],
                widths=0.35,
                color='red',
                labeled_median=True,
                labels_median=[r"$\times$" + str(signif(np.median(bp_algo[i])/np.median(bp_algo[0]),2))
                                     if i>-1 else "" for i in range(4)])
    
  
    
    
    
    ax1.set_ylabel('query resolution time [s]')

    ax1.set_xticks([1,2,3,4])
    
    ax1.set_xticklabels([r'\textsc{BaseEager}$^*$',r'\textsc{BaseLazy}',r'\textsc{BalReq}',
                     r'\textsc{BalLoad}'],
                        rotation=-45,
                        ha="left", rotation_mode="anchor")


    ax1.set_ylim([0, 2600])
    ax1.tick_params(axis='x', which='major', pad=1)

    for i in range(3):
        ax1.plot([i+1.5,i+1.5],[ax1.get_ylim()[0],ax1.get_ylim()[1]],linestyle='--',color='gray',linewidth=1)
    

    ax1.set_xlim([0.5,4.5])
    
    
    ax2 = plt.subplot2grid((1,2),(0,1),colspan=1)
    
    
    baseline_work = loaddata(files_churn[1])
    baseline_work_avg = 1 
    bp_algo2 = []
    
    for i in range(0,4):
        bpdata2 = [x/baseline_work_avg for x in data_algo[i][:,-1]]
        bp_algo2.append(bpdata2)
        
    

    violinify(ax2, [bp_algo2[0],bp_algo2[1],bp_algo2[2],bp_algo2[3]],
                positions = [1-1/5,2-1/5,3-1/5,4-1/5],
                widths=0.35,
                color='red',
                labeled_median=True,
                labels_median=[r"$\times$" + str(signif(np.median(bp_algo2[i])/np.median(bp_algo2[1]),2))
                                     if i!=-1 else "" for i in range(4)])
    
   

    from matplotlib.patches import Patch

    p1 = Patch(facecolor="red", alpha=0.25)

    l1, = ax2.plot([1,1],color="red", linewidth=1)
    ax2.legend([(p1,l1)],[r'\textit{Geolife}'],
        handlelength=1.1,
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        loc=(0.237,0.765))
    l1.set_visible(False)


    
    ax2.yaxis.tick_right()
    ax2.set_ylabel("fleet workload [s]")
    ax2.yaxis.set_label_position("right")
    
    ax2.set_xticks([1,2,3,4])   
    ax2.set_xticklabels([r'\textsc{BaseEager}',r'\textsc{BaseLazy}$^*$',r'\textsc{BalReq}',
                     r'\textsc{BalLoad}'],
                    rotation=-45,
                    ha="left", rotation_mode="anchor")

    ax2.tick_params(axis='x', which='major', pad=1)

    for i in range(3):
        ax2.plot([i+1.5,i+1.5],[ax2.get_ylim()[0],ax2.get_ylim()[1]],linestyle='--',color='gray',linewidth=1)
    
    ax2.set_xlim([0.5,4.5])


    plt.subplots_adjust(wspace=0.05)
    
    plt.savefig('comparison_algorithms_churn.pdf',bbox_inches = 'tight',pad_inches = 0.006)


 

def plot_time_all_churn():
    data_and_ratios = [loaddata_churn(file) for file in files_churn]
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    
    fig,ax = plt.subplots(4,1)
    
    axes = len(data_and_ratios[0][1])
    
    texts = ['(i)','(ii)','(iii)','(iv)']
    
    colors = ['red','green','blue','black']

    textpos = [[0.9,0.18],[0.9,0.18],[0.9,0.65],[0.9,0.65]]

    to_plot = [1,2,3,4,5,6,7]
        
    for i in range(4):
        algo_data = data_and_ratios[i][0]
        for j in range(axes):
            if len(algo_data[j]) == 0:
                algo_data[j].append(0)
        violinify(ax[i],algo_data,
            color=colors[i])
        ax[i].set_yscale('log')
        ax[i].text(*textpos[i],texts[i],
          transform=ax[i].transAxes)
        
    
    ax[3].set_xticklabels([str('$Q_{' + str(i) + '}$') for i in to_plot])
   
    plt.savefig('time_all_beijing_churn.pdf',bbox_inches = 'tight',pad_inches = 0)


def plot_time_all():
    data = [loaddata(file) for file in files]
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    
    fig,ax = plt.subplots(4,1)
    
    to_plot = [0,1,2,3,4,5,6,7,8,9]
    

    
    texts = ['(i)','(ii)','(iii)','(iv)']
    
    colors = ['red','green','blue','black']

    textpos = [[0.9,0.18],[0.9,0.18],[0.9,0.65],[0.9,0.65]]
        
    for i in range(4):
        algo_data = data[i]
        violinify(ax[i],[algo_data[:,i] for i in range(10)],
            color=colors[i])
        ax[i].set_yscale('log')
        ax[i].text(*textpos[i],texts[i],
          transform=ax[i].transAxes)
        
    
    ax[3].set_xticklabels([str('$Q_{' + str(i + 1) + '}$') for i in to_plot])
   
    plt.savefig('time_all_beijing.pdf',bbox_inches = 'tight',pad_inches = 0.014)


