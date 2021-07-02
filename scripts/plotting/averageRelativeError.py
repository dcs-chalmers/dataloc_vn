from violinify import violinify
from latexify import latexify
latexify(columns=1)





from matplotlib import pyplot as plt


fig, ax = plt.subplots(1,1)



from matplotlib.patches import Patch

p1 = Patch(facecolor="red", alpha=0.25)
p2 = Patch(facecolor="green", alpha=0.25)
p3 = Patch(facecolor="blue", alpha=0.25)
p4 = Patch(facecolor="black", alpha=0.25)

l1, = ax.plot([1,1],color="red", linewidth=1)
l2, = ax.plot([1,1],color="green", linewidth=1)
l3, = ax.plot([1,1],color="blue", linewidth=1)
l4, = ax.plot([1,1],color="black", linewidth=1)
ax.legend([(p1,l1), (p2,l2), (p3,l3), (p4,l4)],[r'\textsc{BaseEager}',r'\textsc{BaseLazy}',r'\textsc{BalReq}',
                     r'\textsc{BalLoad}'],
    ncol = 4,
    edgecolor='black',
    facecolor='white',
    framealpha=1,
    borderpad = 0.3,
    handletextpad = 0.3,
    columnspacing = 0.5,
    handlelength = 1.5,
    fontsize = 7,
    loc = (-0.073,1.1))
l1.set_visible(False)
l2.set_visible(False)
l3.set_visible(False)
l4.set_visible(False)


# ----------------------

datapath = "../experiments/error.csv"
data = []

with open(datapath,"r") as f:
	for line in f:
		data.append([float(x) for x in line.split(",")[:-1]])

def getData(algo, N):
	returnedData = []
	for line in data:
		if line[0] ==  algo and line[1] == N:
			returnedData.append((line[2]/0.6+line[3]/0.43+line[4]/0.28+line[5]/0.18+line[6]/0.12)/5)
	return returnedData


for j in range(3):
	violinify(ax, [getData(0, 25*(j+1)) for j in range(3)], positions = [0,5,10], color = "red")
	violinify(ax, [getData(1, 25*(j+1)) for j in range(3)], positions = [1,6,11], color = "green")	
	violinify(ax, [getData(2, 25*(j+1)) for j in range(3)], positions = [2,7,12], color = "blue")
	violinify(ax, [getData(3, 25*(j+1)) for j in range(3)], positions = [3,8,13], color = "black")


ax.set_xlim([-1,14])
ax.set_xticks([1.5,6.5,11.5])
ax.set_xticklabels([r"$n=25$", r"$n=50$", r"$n=75$"])

ax.set_ylim([0,0.7])

ax.plot([4,4],[0,1], color = "gray", linestyle = "--", linewidth = 1)
ax.plot([9,9],[0,1], color = "gray", linestyle = "--", linewidth = 1)

ax.text(-3.6,0.5,r"$\Delta Q\!R / Q\!R$", rotation=90)

ax.text(13.7,0.6,r"\textit{Geolife}", ha="right")



plt.subplots_adjust(hspace=0.15)
plt.savefig("query_relative_errors_2figs.pdf", bbox_inches="tight", pad_inches = 0.01)
