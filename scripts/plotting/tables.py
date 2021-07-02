from boxplot_fast_slow_compare import *
from prettytable import PrettyTable
import numpy as np

def table_summary():
    data_algo = []
    for i in range(0,4):
        data_algo.append(loaddata(files[i]))

    results = []
    for i in range(0,4):
        _result = [np.mean([np.mean(line[:-1]) for line in data_algo[i]]), 
                   np.mean([line[-1] for line in data_algo[i]])]
        results.append(_result)
        

    # convert to seconds
    results_s = [[round(r/1000,2) for r in line] for line in results]


    table = PrettyTable(["algo", "geolife res time [s]", "geolife fleet workload [%]"])


    table.add_row(["baseeager",*results_s[0]])
    table.add_row(["baselazy",*results_s[1]])
    table.add_row(["balreq",*results_s[2]])
    table.add_row(["balload",*results_s[3]])

    print("Summary, STATIC fleet model:")
    with open("table2_static.txt","w") as outf:
        print(table, file=outf)

    print(table)

def table_summary_churn():
    data_algo = []
    for i in range(0,4):
        data_algo.append(loaddata(files_churn[i]))

    results = []
    for i in range(0,4):
        _result = [np.mean([np.mean(remove_numpy_nans(line[:-1])) for line in data_algo[i]]), 
                   np.mean([line[-1] for line in data_algo[i]])]
        results.append(_result)
        

    # round to seconds
    results_r = [[round(r,2) for r in line] for line in results]


    table = PrettyTable(["algo", "geolife res time [s]", "geolife fleet workload [s]"])


    table.add_row(["baseeager",*results_r[0]])
    table.add_row(["baselazy",*results_r[1]])
    table.add_row(["balreq",*results_r[2]])
    table.add_row(["balload",*results_r[3]])
    
    print("Summary, DYNAMIC fleet model:")
    
    with open("table2_dynamic.txt","w") as outf:
        print(table, file=outf)

    print(table)

table_summary()
table_summary_churn()
