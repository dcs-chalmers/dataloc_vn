# Time- and Computation-Efficient Data Localization in Vehicular Networks’ Edge

This repository contains the code required to reproduce the results shown in the titular paper. Furthermore, it enables the user to implement custom data localization algorithms and test them using the authors' query-spreading framework based on real vehicular data.
For evaluating the data localization algorithms, we employ a subset of the GeoLife GPS dataset (1, see bottom) containing only vehicular GPS traces. We describe how to create this dataset in the "First steps" section.

*Please note: the Volvo Cars dataset employed in the publication cannot be publicly disclosed and corresponding evaluations are therefore excluded from this repository.*

## Requirements

The repository has been tested under Ubuntu 16.04 + 20.04. The following dependencies exist:

- Anaconda: `conda` for Python 3.8, installer available [here](https://docs.conda.io/en/latest/miniconda.html)
- `bash 5.x`
- (Optional, but recommended for figure plotting:) TeXLive, installable via `sudo apt-get install texlive-full`

## First steps

1. Clone this repository. All paths in the following are relative to the root of the repository.
2. Setup a `conda` environment with the required Python dependencies: In the root of the repository, execute `conda env create -f requests-env.yml`
3. Activate the `requests` environment for `conda`: `conda activate requests`
4. Download the Microsoft GeoLife dataset from [here](https://www.microsoft.com/en-us/download/details.aspx?id=52367&from=https%3A%2F%2Fresearch.microsoft.com%2Fen-us%2Fdownloads%2Fb16d359d-d164-469e-9fd4-daa38f2b2e13%2F), and extract the `zip` file to a folder of your choice (we will call it `path/to/your/geolife/download`).
5. Enter the folder `scripts/datasets`, and execute the data preprocessing script: `python genbeijing.py path/to/your/geolife/download`. This will remove non-vehicular GPS traces from the GeoLife dataset and concatenate GPS traces from the same road user into a single file for a a single day. The resulting dataset is stored in the folder `datasets/beijing`.

## Automated reproduction of paper results

*Remember to perform Step 3 from First Steps above before running any experiments.*

*Running all experiments takes considerable amounts of time. On a laptop, estimate 12hrs for 1000 repetitions.*

1. Enter the folder `scripts/experiments`: `cd scripts/experiments`
2. Execute the reproduction script, which will run all python scripts inside this folder in the correct order. The standard number of repetitions for each experiment is 1000. 
If you wish to peform fewer or more repetitions, change the value of the parameter `REPETITIONS` in `run_all_experiments.sh`. Then, execute: `bash run_all_experiments.sh`.
*Beware that to model realistic vehicular execution times of the individual queries, `create_q_and_time_for_shortqueries.py` should be executed on near-vehicular hardware.
By default, `run_all_experiments.sh` will execute all code on the machine it was called on.*
3. Enter the plotting folder: `cd ../plotting` (from inside the folder `scripts/experiments`)
4. Plot all figures: `bash plot_all.sh`

Now, the folder `scripts/plotting` contains `pdf` plots for all the figures in the paper, as well as two text files with the summary table\*. The following table maps the figure names in `scripts/plotting` to figure numbers in the paper:

| figure number | pdf name |
| -------- | ------------- |
| 1        | no_vehicles_churn_beijing.pdf |
| 3        | answers_rate_combined.pdf |
| 4        | beijingBalancedAlgoalpha-beta-combined_fleetWorkload.pdf | 
| 5        | time_all_beijing.pdf  |
| 6        | comparison_algorithms.pdf |
| 7        | fairness.pdf |
| 8         | query_estimates_beijing.pdf, query_relative_errors_2figs.pdf |
| 9        | time_all_beijing_churn.pdf|
| 10        | comparison_algorithms_churn.pdf |
| Table 2  | table2_static.txt, table2_dynamic.txt |

\* *We want to remind the reader that we exclude evaluations based on the Volvo Cars dataset, thus only plots pertaining to the GeoLife dataset are shown.*

## Custom experiments

To use the framework for custom experiments, a number of properties of the fleet have to be statically precomputed first. To do this, do the following:

1. Enter the folder `scripts/experiments`
2. Statically precompute the request execution times and answers per-vehicle: `python create_q_and_time_for_shortqueries.py`
3. Statically precompute the availability of single cars: `python create_active_vehicles.py`

Now, you can create custom query spreading algorithms. A blueprint of a query-spreading algorithm is defined in the file `sim.py` in the root of the project: `class QuerySpreadingAlgorithm`. 

To compare your custom algorithm with the algorithms published in the paper for a certain experiment, add the name of your algorithm to the list of algorithms defined in the corresponding experiment script, and execute the script. A list of all experiment scripts is given in `scripts/experiments/run_all_experiments.sh`.

-------------------------
(1) Zheng, Y., Li, Q., Chen, Y., Xie, X., & Ma, W. Y. (2008, September). Understanding mobility based on GPS data. In Proceedings of the 10th international conference on Ubiquitous computing (pp. 312-321).
