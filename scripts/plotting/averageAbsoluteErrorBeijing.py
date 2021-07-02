from latexify import latexify


datapath = "../experiments/error.csv"

import numpy as np

data = []
with open(datapath,"r") as f:
	for line in f:
		data.append([float(x) for x in line.split(",")[:-1]])


Ns = [10,25,50,75,100,125,150,175]


def getData(algo, N, q):
	assert q < 5, "q must be between 0 and 4"
	return [x[q+2] for x in data if x[0] == algo and x[1] == N]


# print(getData(0,100,4))

latexify(columns = 1)

from matplotlib import pyplot as plt


fig, ax = plt.subplots(5,1)


    
for query in range(5):
	ax[query].plot(Ns, [np.mean(getData(0, N, query)) for N in Ns], color = "red", linestyle="--")
	ax[query].plot(Ns, [np.mean(getData(1, N, query)) for N in Ns], color = "green", linestyle = ":")
	ax[query].plot(Ns, [np.mean(getData(2, N, query)) for N in Ns], color = "blue", linestyle = "-")
	ax[query].plot(Ns, [np.mean(getData(3, N, query)) for N in Ns], color = "black", linestyle = "-.")

ax[4].set_xticks(Ns)
ax[4].set_xlabel(r"$n$ (min. number of positive answers required)")

ax[0].legend([r'\textsc{BaseEager}',r'\textsc{BaseLazy}',r'\textsc{BalReq}',r'\textsc{BalLoad}'],
	ncol = 4,
	fancybox="off",
    edgecolor='black',
    facecolor='white',
    framealpha=1,
    borderpad = 0.3,
    handletextpad = 0.3,
    columnspacing = 0.5,
    handlelength = 1.5,
    fontsize = 7,
    loc = (-0.023,1.1))

ax[0].text(172,0.145,r"$Q_1$")
ax[1].text(172,0.10,r"$Q_2$")
ax[2].text(172,0.147,r"$Q_3$")
ax[3].text(172,0.04,r"$Q_4$")
ax[4].text(172,0.08,r"$Q_5$")
ax[4].text(-30,0.145, r"$\Delta Q\!R$", rotation=90)


plt.savefig("query_estimates_beijing.pdf", bbox_inches="tight", pad_inches = 0.01)
