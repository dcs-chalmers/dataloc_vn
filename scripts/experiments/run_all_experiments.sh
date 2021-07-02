REPETITIONS=1000

echo "Will run all required experiments in the correct order."
echo "This may take up to 12 hours (at 1000 repetitions)."

echo "------------------------------------"
echo "--------------S T A R T-------------"
echo "------------------------------------"

# create q.dat, time.dat
echo "1/9 statically pre-computing the time to process requests on vehicles"
python create_q_and_time_for_shortqueries.py beijing

# create size.dat
echo "2/9 calculate data volumes per vehicle"
python create_size_beijing.py

# create vehicles.dat
echo "3/9 statically pre-computing the times during the day certain vehicles are switched on"
python create_active_vehicles.py beijing

# create the alpha.beta-plot-data
echo "4/9 Vary the value of alpha, beta to observe the impact."
echo "CAUTION: this takes considerable amounts of time"
python create_alpha_beta.py beijing $REPETITIONS

# calculate the churn in the dataset
echo "5/9 calculate the churn in the datasets"
python create_churns.py beijing

# calculate the full query response times for the static and dynamic fleet model
echo "6/9 Calulate the full query response times for the STATIC fleet model"
python create_query_response_times.py beijing $REPETITIONS
echo "7/9 Calulate the full query response times for the DYNAMIC fleet model"
python create_query_response_times_dynamic.py beijing $REPETITIONS

# extract the fairness of the algorithms
echo "8/9 Perform repeated experiments to extract the standard deviation of workloads"
python create_fairness.py beijing $REPETITIONS

# check how well the algorithms estimate the true fraction of yes-answers in the whole fleet
echo "9/9 Perform repeated experiments to observe how well the algorithms estimate the true fraction of yes-answers"
python create_estimation.py beijing $REPETITIONS

echo "------------------------------------"
echo "--------------- D O N E-------------"
echo "------------------------------------"