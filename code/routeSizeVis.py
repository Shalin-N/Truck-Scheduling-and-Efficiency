import numpy as np
from numpy.core.fromnumeric import mean
import pandas as pd
import itertools as it
from pulp import *
import os
import time

'''This code simulates random routes of given length and calculates
    what percentage have valid demand '''

if __name__ == "__main__":
    # Read data from Demand Long Pivot (only 1 value for demand in each row)
    initial = pd.read_csv("code" + os.sep + "data" + os.sep + "DemandLongPivot.csv", index_col=0)
    initial.set_index('Store')
    # Take all days that you want
    weekday = initial[initial['day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
    # exclude when demand = 0
    weekday = weekday[weekday['demand']>0]
    # Pivot back so now you have columns for each date (1 row for each store)
    pivoted = weekday.pivot(index = 'Store', columns = 'date', values = 'demand')
    #initialise
    count = 0
    number = 0
    # how many simulations do you want
    daily_sims = 10000
    # length of routes
    testing_number = 5
    # loop through each day
    for j in range(len(pivoted.columns)):
        # generate random values to index from
        randi = np.random.randint(0,pivoted.shape[0],daily_sims + testing_number)
        # for each random value, take 5 demands and add them
        for i in range(daily_sims):
            sums = 0
            for len in range(testing_number):
                sums += pivoted.iloc[randi[i+len],j]
            # add 1 sim
            count += 1
            # if sim is valid, add 1 to valid sims
            if sums < 28:
                number += 1
    print('Viable Routes: ' + str(number))
    print('Total Routes Simulated: ' + str(count))
    print('Percentage Valid: ' + str(number/count))