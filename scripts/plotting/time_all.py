from boxplot_fast_slow_compare import plot_time_all

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["beijing"], type=str, help="Choose which experiment (dataset) to plot.")

args = parser.parse_args()


experiment = args.experiment


if experiment == "beijing":
	plot_time_all()