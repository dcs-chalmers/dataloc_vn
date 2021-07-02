from latexify import latexify
latexify(columns = 1)

from matplotlib import pyplot as plt

def load_dat(filename, axis=1):
    with open(filename, "r") as f:
        return [float(line.split()[axis]) for line in f.readlines()]

def moving_average(data, m=5):
    return [sum(data[i:i+m])/len(data[i:i+m]) for i in range(len(data))]

def average(data):
    return sum(data)/len(data)

def set_xaxis_1day(ax):
    times = list(range(0,25,4))
    ax.set_xticks([100*t/24 for t in times])
    ax.set_xticklabels([f"{t:02d}:00" for t in times])
    

def plot_churn_one_dataset(dataset, interval=60):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    vehicles = load_dat(f"../experiments/{dataset}_{interval}.dat", 2)
    churn = load_dat(f"../experiments/{dataset}_{interval}.dat", 1)
    # arrivals = load_dat(f"../../gnuplot/{dataset}-arrival-1min.dat", 1)
    
    ax.plot(vehicles, label=r"\# of vehicles", marker='.', color="blue",
        linewidth = 1, markersize = 3)

    N = [30,60,300,900] #beijing can add 1,4,5
    #10 can be added as well (but strip for now)
    files = [f"../experiments/{dataset}_{n}.dat" for n in N]


    colors = ["#ff0000","#ff4f4f","#ff6e6e","#fca7a7"] 
    styles = ["dotted","dashed",(0,(3,1,1,1,1,1,1,1)),"-"]
    styles.reverse()
    colors.reverse()      

    for file, n, count in zip(files,N,range(len(N))):
        churn_rates = load_dat(file)
        ax2.plot(moving_average(churn_rates),
                #label=f"{n}s interval" if count == 0 else f"{n}s",
                label = r"$\Delta={}$s".format(n),
                color = colors[count],
                linestyle = styles[count],
                linewidth = 1)


    ax.legend(fancybox="off",
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        borderpad = 0.3,
        handletextpad = 0.3,
        columnspacing = 0.5,
        handlelength = 1.5,
        fontsize = 7,
        loc = (0.01,0.87))
    
    ax2.legend(ncol = 5,
        fancybox="off",
        edgecolor='black',
        facecolor='white',
        framealpha=1,
        borderpad = 0.3,
        handletextpad = 0.3,
        columnspacing = 0.5,
        handlelength = 1.5,
        fontsize = 7,
        loc = (-0.10,1.05))
    
    ax2.set_ylabel(r"Churn$_\Delta (t)$")
    ax.set_ylabel("\# active vehicles")



    set_xaxis_1day(ax)
    # fig.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(f'no_vehicles_churn_{dataset}.pdf', bbox_inches="tight", pad_inches = 0.01)





#plot_no_vehicles()
plot_churn_one_dataset("beijing")
