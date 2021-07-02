from latexify import latexify
latexify(columns = 1, fig_height=1.6)

from violinify import violinify

from matplotlib import pyplot as plt

def loadcsv(filename):
    with open(filename,"r") as f:
        return [[float(x)*1000 for x in l.strip().split(',')] for l in f.readlines()]


fairness = loadcsv("../experiments/fairness.csv")
# fairnessv = loadcsv("../experiments/fairnessv.csv")

labels = [r'\textsc{BaseEager}',r'\textsc{BaseLazy}',r'\textsc{BalReq}',
                     r'\textsc{BalLoad}']

X = [1.5*x for x in range(4)]
space = 0.3


fig, ax = plt.subplots()

with open("../experiments/baseline1fairness.csv", "r") as f:
    fair1 = float(f.readline().strip()) * 1000

violinify(ax, [[fair1]]+[[fair[i] for fair in fairness] for i in range(3)],
    positions = [x-space for x in X],
    color = "red")



# with open("../experiments/baseline1fairnessv.csv", "r") as f:
#     fairv1 = float(f.readline().strip()) * 1000

# violinify(ax, [[fairv1]]+[[fair[i] for fair in fairnessv] for i in range(3)],
#     positions = [x+space for x in X],
#     color = "blue")

from matplotlib.patches import Patch


p1 = Patch(facecolor="red", alpha=0.25)
# p2 = Patch(facecolor="blue", alpha=0.25)

l1, = ax.plot([1,1],color="red", linewidth=1)
# l2, = ax.plot([1,1],color="blue", linewidth=1)
ax.legend([(p1,l1)],[r'\textit{Geolife}'],
    handlelength=1.1,
    # fancybox=False,
    edgecolor='black',
    facecolor='white',
    framealpha=1,
    loc="best")
l1.set_visible(False)
# l2.set_visible(False)

max_y = ax.get_ylim()[1]

for i in range(3):
    ax.plot([1.5*i+0.75,1.5*i+0.75],[0,max_y],linestyle='--',color='gray',linewidth=1)


# legend_elements = [Patch(facecolor="red"), Patch(facecolor="blue")]
# ax.legend(ncol = 2,
#     fancybox="off",
#     edgecolor='black',
#     facecolor='white',
#     framealpha=1,
#     borderpad = 0.3,
#     handletextpad = 0.3,
#     columnspacing = 0.5,
#     handlelength = 1.5,
#     fontsize = 7,
#     loc = (0.55,0.85))



ax.set_xlim([-0.7,5.2])

ax.set_xticks(X)
ax.set_xticklabels(labels)


ax.set_ylabel(r"$\sigma_{load}$ [ms]")


fig.tight_layout()
fig.savefig('fairness.pdf', bbox_inches="tight", pad_inches = 0.01)