import os
import numpy as np
from datetime import datetime

now = datetime.now().strftime("%d%m%Y-%H%M%S")

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing",], type=str, help="Choose which experiment (dataset) to plot.")

args = parser.parse_args()

def genFilenames(folder,keyword):
    for file in os.listdir(folder):
        if keyword in file:
            yield os.path.join(folder,file)
            

def loadPlotDataMaxTime(filenames):
    x = []
    y = []
    s = []
    for file in filenames:
        try:
            alpha = float(file.split("alpha=")[1].split("_beta")[0])
            beta  = float(file.split("beta=")[1])
            data  = np.loadtxt(file,delimiter=",")
            value = np.mean([np.max(data[i,:-1]) for i in range(len(data[:,1])-1)])
            
            # since beta = 1 could incure infinite waiting time, we explude it
            if beta == 1:
                continue

            x.append(alpha)
            y.append(beta)
            s.append(value)
        except:
            print("OOPS, problem with", file)
            
    return x,y,s

def loadPlotDataWork(filenames):
    x = []
    y = []
    s = []
    for file in filenames:
        try:
            alpha = float(file.split("alpha=")[1].split("_beta")[0])
            beta  = float(file.split("beta=")[1])
            data  = np.loadtxt(file,delimiter=",")
            value = data[-1,-1]
            
            # since beta = 1 could incure infinite waiting time, we explude it
            if beta == 1:
                continue

            x.append(alpha)
            y.append(beta)
            s.append(value)
        except:
            print("OOPS, problem with", file)
    
    return x,y,s

def plotMaxTime(folder,algo):
    x,y,s = loadPlotDataMaxTime(genFilenames(folder,algo))
    scalefactor = 100 # max size of points
    max_s = max(s)
    min_s = min(s)
    s_scaled = [((si-min_s)/(max_s-min_s)+0.1)*scalefactor for si in s]
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    fig,ax = plt.subplots()
    ax.scatter(x,y,s_scaled,color="red")
    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel(r"$\beta$")
    ax.set_title("maxTime")
    plt.savefig(algo + "alpha-beta-time.pdf",bbox_inches = 'tight',pad_inches = 0)
    
    
def plotWork(folder,algo):
    x,y,s = loadPlotDataWork(genFilenames(folder,algo))
    scalefactor = 100 # max size of points
    max_s = max(s)
    min_s = min(s)
    s_scaled = [((si-min_s)/(max_s-min_s)+0.1)*scalefactor for si in s]
    
    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    fig,ax = plt.subplots()
    ax.scatter(x,y,s_scaled,color="blue")
    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel(r"$\beta$")
    ax.set_title("work")
    plt.savefig(algo + "alpha-beta-work.pdf",bbox_inches = 'tight',pad_inches = 0)
       
    
def combinedPlot(folder,algo,title):
    
    offset = 0.05
    alpha  = 1
    
    x,y,s = loadPlotDataMaxTime(genFilenames(folder,algo))
    scalefactor = 100 # max size of points
    max_s = max(s)
    min_s = min(s)
    #s_scaled = [((si-min_s)/(max_s-min_s)+0.1)*scalefactor for si in s]
    s_scaled = [1 + (si-min_s)/(max_s-min_s) * scalefactor for si in s]


    from latexify import latexify
    latexify(columns=1)
    from matplotlib import pyplot as plt
    fig,ax = plt.subplots()
    
    x = [xi-offset for xi in x]
    ax.scatter(x,y,s_scaled,facecolors="red",label = "max query time", alpha = alpha, edgecolors = "none")
    
    x,y,s = loadPlotDataWork(genFilenames(folder,algo))
    scalefactor = 100 # max size of points
    max_s = max(s)
    min_s = min(s)
    #s_scaled = [((si-min_s)/(max_s-min_s)+0.1)*scalefactor for si in s]
    s_scaled = [1 + (si-min_s)/(max_s-min_s) * scalefactor for si in s]


    x = [xi+offset for xi in x]
    ax.scatter(x,y,s_scaled,facecolors="blue",label = "analysis cost", alpha = alpha, edgecolors = "none")
    
    ax.set_title("combined")
    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel(r"$\beta$")
    ax.legend(
            ncol = 2,
            fancybox="off",
            edgecolor='black',
            facecolor='white',
            framealpha=1,
            loc=(0.05,1.01)
            )
    
    ax.set_xticks([0.25,0.5,.75,1,1.25,1.5,1.75,2])
    ax.set_yticks([0,.1,.2,.3,.4,.5,.6,.7,.8,.9])
    
    plt.savefig(title + algo + "alpha-beta-combined.pdf",bbox_inches = 'tight',pad_inches = 0)



experiment = args.experiment


folderpath = f"../experiments/alpha_beta_{experiment}_balancedAlgo_shortqueries"
combinedPlot(folderpath,"BalancedAlgo",experiment)
    
    
    
    
    
    
    
    
    
    
