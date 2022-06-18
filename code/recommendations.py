import itertools as it
import os
from typing import Mapping

import numpy as np
import pandas as pd
from pulp import *
from scipy import stats

from generate_demands import *
import matplotlib.pyplot as plt
import copy
from Routes import *

def vehicleRoutingProblemR(max, droppeddf, weekend = False, Mapping = False):
    """ solve a vehicle routing problem for specific demands and a maximum route size.
            Parameters:
            -----------
            col : int
                the maximum amount of stores per route.
            
            Weekend : bool
                True if we are generating saturday routes, false by default.


            Notes:
            ------
            This is a wrapper for all other functions in this file.
    """
    
    # instantiation of tracking variables
    bestRoutes = []
    bestTimes = []
    totalTime = 0

    # read in demands
    demands = readDemands(int(weekend))

    for row in droppeddf.index:
        demands.loc[droppeddf['Merged'][row]] += demands.loc[droppeddf['Dropped'][row]] * droppeddf['%'][row]
        print(droppeddf['Dropped'][row])
        if weekend:
            print(droppeddf['SatRegion'][row])
        else:
            print(droppeddf['Region'][row])
        print(demands.loc[droppeddf['Dropped'][row]] * (1-droppeddf['%'][row]))
        if demands.loc[droppeddf['Merged'][row]] > 9.8:
            demands.loc[droppeddf['Merged'][row]] += -1
        demands.drop(droppeddf['Dropped'][row], inplace = True)

    #demands = generate_demands(type = 'Ceil', Saturday=weekend)

    # set regions depending on if weekend or weekday
    if weekend:
        regionAreas = ["North", "City", "East", "South", "West", "Central"] 
    else:
        regionAreas = ["North", "City", "East", "SouthEast", "South", "West", "NorthWest"]
    


    # loop through each region
    for i in regionAreas:
        # select correct region
        region = selectRegion(i, weekend)
        for storedropped in droppeddf['Dropped']:
            if (region.index == storedropped).any():
                region.drop(storedropped, inplace = True)
        # currently not in use
        # if weekend remove 0 demand stores
        #if weekend:
        #    region = checkWeekend(region)

        # generate and cull routes
        routes = routeGeneration(region, max)
        routes = checkDemands(routes, demands)

        # convert route vectors to store lists
        routeNames = routeLocations(routes)

        # instantiate cost vector
        costV = []
        orderV = []

        # loop through routeNames
        for r in routeNames:
            # permutate routes
            permutations = permutateRoute(r)

            cost = 9999999999
            # loop through permutations
            for p in permutations:
                # find cost of permutation
                test = costRoutes(p, demands)

                # store lowest permutation and best order
                if (test < cost):
                    cost = test
                    order = p

            # append lowest cost and best order to vector
            costV.append(cost)
            orderV.append(order)

        # convert vectors to series
        mapping = pd.Series(orderV, index=routes.columns)
        costs = pd.Series(costV, index=routes.columns)

        # select best combination of routes
        prob = routeSelection(routes, costs, i)

        # check, display and store current region
        bestRoutes, bestTimes, check = bestRegion(bestRoutes, bestTimes, prob, mapping, costs)

        # display regions solution
        print(i, check, '/', len(routes.index), "\tcumulative time for region:", value(prob.objective))

        # calculate total time
        totalTime += value(prob.objective)

    # nice clean display of best routes
    display(bestRoutes, bestTimes, totalTime)

    ''' Broken helper function
    if Mapping:
        if weekend:
            visual_all_routes(bestRoutes, 'Saturday')
        else:
            visual_all_routes(bestRoutes, 'Week')
    '''

    return

if __name__ == '__main__':
    #Stores to merge
    stores_tested = [['SuperValue Papakura', 'Countdown Papakura', 0.5, 'SouthEast', 'None'],
            ['Countdown Manukau', 'Countdown Manukau Mall', 2/3, 'SouthEast', 'South'],
            ['Countdown Mt Wellington', 'Countdown Sylvia Park', 0.75, 'South', 'East'],
            ['Countdown Aviemore Drive', 'Countdown Highland Park', 1, 'East', 'East'],
            ['SuperValue Avondale', 'Countdown Lynmall', 0.625, 'West', 'None'],
            ['FreshChoice Glen Eden', 'Countdown Kelston', 0.75, 'West', 'None'],
            ['SuperValue Palomino', 'Countdown Henderson', 0.75, 'NorthWest', 'None'],
            ['Countdown Metro Halsey Street', 'Countdown Metro Albert Street', 2/3, 'City', 'None'],
            ['Countdown Takapuna', 'Countdown Hauraki Corner', 2/3, 'North', 'North'],
            ['Countdown Northwest', 'Countdown Westgate', 0.75, 'NorthWest', 'West']
            ]
    droppedstoresdf = pd.DataFrame(stores_tested, columns = ['Dropped', 'Merged', '%', 'Region', 'SatRegion'])
    vehicleRoutingProblemR(3, droppedstoresdf, weekend = False)
    vehicleRoutingProblem(4, weekend = True)