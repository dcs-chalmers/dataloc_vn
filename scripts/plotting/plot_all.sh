
# plot the churn in the datasets
python vehicles_churn_plot.py 

# plot answer rate vs data volume
python answer_rate.py 

# plot the alpha-beta plot for selection of algorith parameters
python alpha-beta-plot.py beijing 
 
# plot the query resolution times in the static model
python time_all.py beijing 
 
# plot a comparison of algorithms in the static model
python comparison_algorithms.py   

# plt the distribution of work standard deviation within the fleet
python standardDeviationWork.py 

# plot the estimation of true share of yes-answers in the fleet
python averageAbsoluteErrorBeijing.py 

python averageRelativeError.py 

# plot the query resolution times in the dynamic model
python time_all_churn.py beijing 

# plot a comparison of algorithms in the dynamic model
python comparison_algorithms_churn.py 

# create Table2, a summary table
python tables.py