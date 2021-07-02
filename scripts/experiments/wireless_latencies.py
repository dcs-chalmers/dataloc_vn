from scipy.stats import gamma
from collections import defaultdict
import random


class Ofcom2014_gamma():
	'''
	generate and sample from a distribution of 4G latencies as experimentally
	discovered in http://static.ofcom.org.uk/static/research/mbb.pdf, page 49

	usage:
	myOFC = Ofcom2014_gamma()
	latency = myOFC.get_sampler()

	latency()  <--- this will return a latency randomly drawn from the distribution

	'''
	def __init__(self):
		self.size = 100000
		a = 8
		scale=5
		loc=20
		data_gamma = gamma.rvs(a=a, size=self.size, scale=scale, loc=loc)

		minimum = min(data_gamma)
		data_gamma = [x-minimum+20 for x in data_gamma]
		self.dist = data_gamma

	def get_sampler(self):
		return lambda : random.sample(self.dist,1)[0]

	def print_dist(self):
		import numpy as np
		from matplotlib import pyplot as plt
		import sys
		sys.path.append("../plotting")
		from latexify import latexify
		latexify(columns = 1, fig_height=1.5)

		my_bins = [(20,40),(40,60),(60,80),(80,100),(100,200)]

		pre_percentages = defaultdict(int)


		for value in self.dist:
			for my_bin in my_bins:
				begin_bin, end_bin = my_bin
				if begin_bin <= value < end_bin:
					pre_percentages[my_bin] += 1

		percentages = {key : pre_percentages[key]/self.size * 100 for key in pre_percentages.keys()}


		for key in sorted(list(percentages.keys()),key = lambda x: x[0]):
			print(f"{key}: \t {round(percentages[key])}%")

		average = sum(self.dist)/len(self.dist)

		print(f"average: {average}")

		plt.hist(self.dist, 50, weights=np.zeros_like(self.dist) + 1. / len(self.dist), color="blue", alpha=0.3)
		maxy = plt.gca().get_ylim()[1]
		plt.plot([average,average],[0,maxy], color="black", linewidth=1, linestyle="--")
		plt.text(average+1,maxy/14 ,f"average: {int(average)} ms",{"rotation":"vertical","color":"black"})
		plt.xlabel(r"latency [ms]")
		plt.ylabel(r"relative frequency")
		plt.xlim([20,120])
		plt.tight_layout()
		plt.savefig("wireless_latencies.pdf", bbox_inches="tight", pad_inches = 0.01)