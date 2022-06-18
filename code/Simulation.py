import pandas as pd
import os
import copy
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
from generate_demands import demandEstimation3
from Routes import costRoutes
import numpy as np

def simulateRoute(n, weekend=False):
    """ Reads in set of best routes from csv and simulates costs under set of random demands and traffic conditions.
            Parameters:
            -----------
            n : int
                Number of simulations, should be > 30

            weekend : bool
                weekend (true/false)


            Notes:
            ------
            Runs simulations for deterministic routes and t

    """
    # N is intended to be greater than 30
    if n < 30:
        print("\nNumber of simulations should be larger than 30")
        return

    # read in files
    travel_durations = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsTravelDurations.csv", index_col=0)
    routeRegions = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsLocationsDivisions.csv", index_col=2)

    bestRoutesList, bestRoutesDF, bestTimes = read(weekend)
    bestTimesInitial = bestTimes[:-1]

    # read initial demands
    initial_demands = pd.read_csv("code" + os.sep + "data" + os.sep + "DemandLongPivot.csv", index_col=0)

    # df that tracks how many times a store gets dropped from routes
    times_dropped = pd.DataFrame({'Store': list(bestRoutesDF.index), 'Times Dropped': [0] * len(bestRoutesDF)})
    times_dropped.set_index('Store', inplace=True)

    # df that tracks how many times a route is perfect
    times_perfect = pd.DataFrame(
        {'Route': list(bestRoutesDF.columns), 'Times Perfect': [0] * len(list(bestRoutesDF.columns))})
    times_perfect.set_index('Route', inplace=True)

    allcosts = [0] * n

    # run simulation n times
    for sim in range(n):

        # got to be careful here as pivoting can lead to stores being grouped alphabetically or by
        # type which changes relative location of Countdown Metros

        # New copy of best times
        bestTimesCopy = copy.deepcopy(bestTimesInitial)

        # currently outputs in alphabetical order
        demand = demandEstimation3(initial_demands, type='Random', Saturday=weekend)
        droppedstores = []

        # loop through each best route
        for route in bestRoutesDF:
            # generate demands of each route
            demandroute = bestRoutesDF[route].dot(demand.to_list())
            route_list = copy.deepcopy(bestRoutesList[int(route)])

            # check for feasible
            if demandroute <= 26:
                times_perfect.loc[route] += 1
            while demandroute > 26:
                closest_store = 'None'
                closest_store_distance = 999999999

                for store in route_list[1:-1]:
                    if travel_durations['Distribution Centre Auckland'][store] < closest_store_distance:
                        closest_store = store
                        closest_store_distance = travel_durations['Distribution Centre Auckland'][store]

                # append closest store to dropped ones and record
                droppedstores.append(closest_store)
                times_dropped.loc[closest_store] += 1

                index_store = route_list.index(closest_store)
                prev_store = route_list[index_store - 1]
                next_store = route_list[index_store + 1]

                # get new time of route, minus one store
                bestTimesCopy[int(route)] = [int(bestTimesCopy[int(route)]
                                                 - travel_durations.loc[prev_store, closest_store]
                                                 - travel_durations.loc[closest_store, next_store]
                                                 - demand[closest_store] * 450
                                                 + travel_durations.loc[prev_store, next_store])]

                # We round the travel time to the nearest second for indexing issue.

                demandroute += -demand[closest_store]
                route_list.remove(closest_store)

        droppedregions = []
        droppedstoresregion = []

        for dropped in droppedstores:
            if weekend:
                storeregion = routeRegions.loc[dropped]['SatArea']
                if storeregion not in droppedregions:
                    droppedregions.append(storeregion)
            else:
                storeregion = routeRegions.loc[dropped]['Area']
                if storeregion not in droppedregions:
                    droppedregions.append(storeregion)
            droppedstoresregion.append(storeregion)

        droppeddf = pd.DataFrame({'Store': droppedstores, 'Region': droppedstoresregion})
        droppeddf.set_index('Store', inplace=True)

        # Commence wizardry
        for region in droppedregions:
            while len(droppeddf[droppeddf['Region'] == region].index) > 0:
                dontmove = True
                newroutedemand = 0
                newroutetime = 0
                currentstore = travel_durations.loc[droppeddf[droppeddf['Region'] == region].index, \
                                                    'Distribution Centre Auckland'].idxmin()
                droppeddf.drop(currentstore, inplace=True)
                newroute = (currentstore,)
                newroutedemand += demand[currentstore]
                while dontmove and (len(droppeddf[droppeddf['Region'] == region].index) > 0):
                    nextstore = travel_durations.loc[droppeddf[droppeddf['Region'] == region].index, \
                                                     currentstore].idxmin()
                    if (demand[nextstore] + newroutedemand) < 26:
                        newroute += (nextstore,)
                        newroutedemand += demand[nextstore]
                        currentstore = nextstore
                        droppeddf.drop(currentstore, inplace=True)
                    else:
                        dontmove = False
                newroutetime = costRoutes(newroute, demand, morethan4hours=True)
                bestTimesCopy.append(newroutetime)
                # probably don't need this
                # bestRoutes.append(newroute)

        # print("Demands Cut, new cost:")
        allcosts[sim] = simulateRouteIndividual(bestTimesCopy)[0]  # Move t

    times_perfect['Percent Perfect'] = times_perfect['Times Perfect'] / n
    times_dropped['Percent Dropped'] = (times_dropped['Times Dropped'] / n) * 100

    return allcosts, times_dropped, times_perfect


def read(weekend):
    """ Read the deterministic stuff in
            Parameters:
            -----------
            weekend : bool
                True if we are generating saturday routes, false by default.


            Returns:
            --------
            bestRoutesList : list
                list of best routes

            bestRoutesDF : Data Frame
                Data frame of best routes

            bestTimes : array-like
                Array of best times associated with best routes


            Notes:
            ------
            reads both csv and .txt files
    """
    # check for weekend
    if weekend:
        # convert .txt to list of lists
        bestRoutesList = convertToList(weekend)

        # read in files
        bestTimes = pd.read_csv('times_weekend.txt', header = None).values.tolist()
        bestRoutesDF = pd.read_csv("routes_weekend.csv")
    else:
        # convert .txt to list of lists
        bestRoutesList = convertToList(weekend)

        # read in files
        bestTimes = pd.read_csv('times_weekday.txt', header = None).values.tolist()
        bestRoutesDF = pd.read_csv("routes_weekday.csv")

    bestRoutesDF.set_index('Store', inplace=True)

    return bestRoutesList, bestRoutesDF, bestTimes


def convertToList(weekend):
    """ Convert a txt file to a list of lists
            Parameters:
            -----------
            weekend : bool
                weekend (true/false)


            Returns:
            --------
            bestRoutesList : list
                list of best routes


            Notes:
            ------
            reads both the .txt file to a list of lists
    """
    # check for weekend
    if weekend:
        routes = open("routes_weekend.txt", 'r')
    else:
        routes = open("routes_weekday.txt", 'r')


    bestRoutesList = []

    # conversion of each line to list
    for ele in routes:
        ele = ele.replace('\n', '')
        line = ele.split(',')
        bestRoutesList.append(line)

    return bestRoutesList


def simulateRouteIndividual(bestTimes):
    """ Helper function for multiprocessing - appends new total cost to costs list.

    """

    # Simulated cost
    cost = 0

    # Traffic
    for time in bestTimes:
        # -10 minutes/plus 25 minutes
        time += logNormalTraffic() * 60
        if time < 14400:
            cost += time * 225 / 3600
        else:
            cost += 900
            cost += (time - 14400) * 275 / 3600

    return cost


def simulateTraffic(a, m, b):
    """ Simulates random amount of traffic to add to travel times.
        Currently simulates times according to Beta distribution (thanks kevin).
            Parameters:
            -----------
            a : float
                Minimum

            m : float
                Mode

            b : float
                Maximum


            Returns:
            --------
            time : float
                Simulated traffic plus/minus (seconds)

    """
    alpha, beta = alphaBetaFromAmB(a, m, b)
    location = a
    scale = b - a

    taskTime = stats.beta.rvs(alpha, beta) * scale + location

    return taskTime


def alphaBetaFromAmB(a, m, b):
    # Taken from code by David L. Mueller

    # github dlmueller/PERT-Beta-Python
    first_numer_alpha = 2.0 * (b + 4 * m - 5 * a)
    first_numer_beta = 2.0 * (5 * b - 4 * m - a)
    first_denom = 3.0 * (b - a)
    second_numer = (m - a) * (b - m)
    second_denom = (b - a) ** 2
    second = (1 + 4 * (second_numer / second_denom))
    alpha = (first_numer_alpha / first_denom) * second
    beta = (first_numer_beta / first_denom) * second

    return alpha, beta


def summary(costs, dropped, perfect, weekend = False):
    """
    Summary Statistics passed in from simulateRoutes
    """
    n = len(costs)

    # Sorting @ basic summary
    costs.sort()
    twofive = costs[round(n *0.025)]
    nineseven = costs[round(n*0.975)]
    print("\nCentral 95% interval",np.round(twofive,2),"->", np.round(nineseven,2))
    print("Average cost = $",np.round(np.mean(costs),2))

    # Hist of results 
    plt.clf()
    plt.style.use('ggplot')
    kde = stats.gaussian_kde(costs)

    plt.hist(costs, alpha = 0.8, rwidth = 0.94, bins = 25, density=True)
    x = np.linspace(costs[1]-1,costs[-1]+1,1000)
    plt.plot(x, kde(x), color = 'Red')
    plt.axvline(x = costs[int(0.025*n)], color = 'Black')
    plt.axvline(x = costs[int(0.975*n)], color = 'Black')
    plt.axvline(x = np.mean(costs), color = 'Blue')
    plt.xlabel('Total cost, $')
    plt.ylabel('Density')
    # plt.legend([Line2D([0], [0], color='Blue', lw=4)], ['Gaussian Kernal Density estimate'])
    if weekend:
        plt.title("Density hist of simulated costs, Saturday")
        plt.savefig('WeekendSim.png')
    else :
        plt.title("Density hist of simulated costs, Mon-Fri")     
        plt.savefig('WeekdaySim.png') 


    # plt.show()
    
    
    # Summary dropped stats
    dropped = dropped.sort_values(by = ['Times Dropped'], ascending = False)
    print(tabulate(dropped[dropped>0].dropna(), headers=['Number of times dropped','Percent of times dropped']))
    
def logNormalTest(mu = 2.3, sigma = .5, C = 8, S = 0.8):
    '''
    General random traffic offset from a lognormal distribution, plot histogram.
    For testing/calibration purposes.
    '''
    
    
    s = (np.random.lognormal(mu, sigma, 10000) - C) * S

    count, bins, ignored = plt.hist(s, 100, density=True, align='mid')
    plt.xlabel("Time, minutes")
    plt.title("n = 10000")
    plt.axis('tight')
    plt.show()
    plt.savefig("logNormalTest.png")

    print("p x > 30 -> ", sum(i > 30 for i in s)/10000)
    print("p x > 20 -> ", sum(i > 20 for i in s)/10000)
    print("p x > 10 -> ", sum(i > 10 for i in s)/10000)
    print("p x > 0 -> ", sum(i > 0 for i in s)/10000)
    print("p x < -5 -> ", sum(i < -5 for i in s)/10000)

def logNormalTraffic(mu = 2.3, sigma = .5, C = 8, S = 0.8):
    '''
    Generate single random variable for traffic.
    '''
    s = (np.random.lognormal(mu, sigma, 1) - C) * S
    return s
