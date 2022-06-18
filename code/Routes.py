import itertools as it
from pulp import *
from generate_demands import *
from Visualisations import *

def vehicleRoutingProblem(max, weekend = False, Mapping = False):
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
    write(bestRoutes, bestTimes, totalTime, weekend)

    if Mapping:
        if weekend:
            visualise_all_routes(bestRoutes, 'Saturday')
        else:
            visualise_all_routes(bestRoutes, 'Week')

    return


def readDemands(col):
    """ Reads in demands from a csv file and return correct set.
            Parameters:
            -----------
            col : int
                specifies which set of demands (Weekday or Saturday).


            Returns:
            --------
            StoreDemands : Pandas Series
                series of storesNames matched with a demand value.


            Notes:
            ------
            The format of the csv is:
                                    D1, D2

            Store 1                 [10, 11]
            Store 2                 [5, 7]
            Store 3                 [3, 8]
            Store 4                 [6, 9]
    """
    # this is currently hard coded

    demands = pd.read_csv("code" + os.sep + "data" + os.sep + "DemandEstimation.csv", index_col=0)

    return demands[str(col)]


def selectRegion(region, Saturday=False):
    """ return correct set of stores according to specified regions.
            Parameters:
            -----------
            region : string
                specifies which region.


            Returns:
            --------
            storeNames : pandas Series
                series of storesNames according to a region.


            Notes:
            ------
            The format of the csv is:
                         ... Area ...

            Store 1      ... [North] ...
            Store 2      ... [City] ...
            Store 3      ... [South] ...
            Store 4      ... [NorthWest] ...
    """
    areas = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsLocationsDivisions.csv", index_col=2)

    # If a saturday, return the Saturday areas as opposed to normal areas
    if Saturday:
        return areas[areas["SatArea"]==region]

    return areas[areas["Area"]==region]


def checkWeekend(region):
    """ reads through a set of stores and removes all that are not countdown.
            Parameters:
            -----------
            region : pandas DataFrame
                Stores within this region.


            Returns:
            --------
            region : pandas DataFrame
                Culled stores within this region.


            Notes:
            ------
            Superseded by better data storage but left in code incase needed in the future
    """
    for store in region.index:
        test = region['Type'][store]
        if region['Type'][store] != "Countdown":
            region.drop(store, inplace=True, axis=0)

    return region


def routeGeneration(region, choose):
    """ Generate routes of choose! {4,3,2,1} according to a region.
            Parameters:
            -----------
            region : pandas DataFrame
                Stores within this region.

            choose : int
                Max amount of stores per route.


            Returns:
            --------
            routesF : DataFrame
                Series of storesNames according to a region.


            Notes:
            ------

    """

    # get amount of stores in this region
    n = len(region.index)

    # route generation
    routes = np.array(
        [
            [1 if i in comb else 0 for i in range(n)]
            for comb in it.combinations(np.arange(n), choose)
        ]
    )
    for j in range(choose - 1, 0, -1):
        routesJ = np.array([
            [1 if i in comb else 0 for i in range(n)]
            for comb in it.combinations(np.arange(n), j)])
        routes = np.concatenate((routes, routesJ), axis=0)

    # instantiate an empty dataframe
    routesF = pd.DataFrame()

    # loop through each route
    for i in range(len(routes)):

        # transpose and convert routes to series and then append to frame
        copy = pd.Series(routes[i, :].T, index=region.index)
        routesF.insert(i, "Route " + str(i), copy)

    return routesF


def checkDemands(routes, demands):
    """ checks total demand for a set of routes and removes all greater than 26.
            Parameters:
            -----------
            routes : pandas DataFrame
                combination of routes for a selection of stores.

            demands : pandas DataFrame
                Series of demand value indexed with stores.


            Returns:
            --------
            routes : DataFrame
                culled combination of routes for a selection of stores.
    """

    # loop through all routes
    for route in routes:

        # if total demand of route is greater than 26
        if routes[route].dot(demands[routes.index]) > 26:
            # drop current route
            routes.drop(route, inplace=True, axis=1)

    return routes


def routeLocations(routes):
    """ converts the route DataFrame to a list of lists.
            Parameters:
            -----------
            routes : pandas DataFrame
                combination of routes for a selection of stores.


            Returns:
            --------
            routeNames : list of lists
                list of lists containing only the stores within each route.
    """
    # instantiate route names list
    routeNames = []

    #loop through all routes
    for i in routes.columns:

        # convert binary value to a list of store
        temp = [j if routes[i][j] == 1 else 0 for j in routes.index]
        temp = list(filter(lambda a: a != 0, temp))

        # append the route name list
        routeNames.append(temp)

    return routeNames


def permutateRoute(route):
    """ generates permutations of each route.
            Parameters:
            -----------
            route : list
                list containing only the stores within route.


            Returns:
            --------
            permutations : object(tuple)
                permutations of stores within route.


            Notes:
            ------
            Assuming unidirectional so ABCD == DCBA
    """
    return it.permutations(route)


def costRoutes(route, demands, morethan4hours = False):
    """ cost routes according to store order.
            Parameters:
            -----------
            route : tuple
                combination of stores.
            demands : 
                Series of demand information


            Returns:
            --------
            cost : int
                final cost of a route


            Notes:
            ------
            We don't need an unidirectional average even though the times are directional
            During simulation we will generate values that range over both directions times

                   t1 -- t2
            simt1------------simt2
        <---------------------------->
                   continuum
    """
    cost = 0

    # read in time DataFrame with storeName indexing
    if PATHFILE:
        time = pd.read_csv("code" + os.sep + "data" +os.sep +"WoolworthsTravelDurations.csv", index_col=0)
    else:
        time = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv", index_col=0)

    # Setting time to zero for demand = 0
    for store in range(len(route)):
        cost += 450 * demands[route[store]]

    # insert origin node at start and end
    route = ('Distribution Centre Auckland',) + route + ('Distribution Centre Auckland',)

    # loop from 1 through length of route list
    for i in range(1, len(route)):
        # add time between current and previous node
        cost += time[route[i]][route[i-1]]

    # ignore routes longer than 4 hours
    if not morethan4hours:
        if (cost > 14400):
            cost = 99999

    return cost


def routeSelection(routesFrame, timeFrame, region):
    """ Select the best combination of routes that satisfy each store
            Parameters:
            -----------
            routesFrame : Pandas DataFrame
                collection of routes for each store.

            timeFrame : Pandas Series
                contains the time associated with each route.

            region: string
                specifies the current region


            Returns:
            --------
            prob : object
                object containing everything regarding to the lp solution


            Notes:
            ------
            This function uses an integer linear program to solve for the best selection of routes

            The routeFrame format is:
                                    R1,R2,R3,R4,R5

            Store 1                 [1, 1, 1, 0, 1]
            Store 2                 [0, 0, 1, 1, 0]
            Store 3                 [1, 0, 0, 1, 1]
            Store 4                 [0, 1, 1, 0, 1]

            The timeFrame format is:
            Time per route [100, 36, 57, 69]
    """
    # create problem and variables
    prob = LpProblem(region, LpMinimize)
    vars = LpVariable.dicts(region, routesFrame.columns, 0, None, 'Integer')

    # objective constraints
    prob += lpSum([vars[i] * timeFrame[i] for i in timeFrame.index]), "Time"

    # route constraints
    for i in routesFrame.index:
        prob += lpSum([vars[j] * routesFrame[j][i] for j in routesFrame.columns]) == 1

    prob += lpSum([vars[i] for i in routesFrame.columns]) <= 30

    # The problem data is written to an .lp file
    # prob.writeLP("VehicleRoutingProblem.lp")

    # The problem is solved using PuLP's choice of Solver, msg=0 to suppress output
    prob.solve(PULP_CBC_CMD(msg=0))

    return prob


def bestRegion(bestRoutes, bestTimes, prob, mapping, costs):
    """ Helper function to check and prepare routes and time data for display
            Parameters:
            -----------
            bestRoutes : Pandas DataFrame
                contains the best routes that satisfy all store demands.

            bestTimes : Pandas Series
                contains the best time associated with a route permutation.

            prob : object
                object containing everything regarding to the lp solution.

            mapping : list
                contains all the route data for a region.

            costs : list
                contains all the time data for a region.


            Returns:
            --------
            bestRoutes : Pandas DataFrame
                contains the updated best routes that satisfy all store demands.

            bestTimes : Pandas Series
                contains the updated best time associated with a route permutation.

            check : int
                counter to check if all stores where visited.
    """
    # loop through problem variables
    check = 0
    for v in prob.variables():
        # only transform used routes
        if (v.varValue != 0):
            # convert problem variable regions to correct index format
            str = v.name.split("_", 1)[1].replace("_", " ")

            # check each store is satisfied
            check += 1 * len(mapping.loc[str])

            # store in vector for final display
            bestRoutes.append(mapping.loc[str])
            bestTimes.append(costs.loc[str])

    return bestRoutes, bestTimes, check


def display (bestRoutes, bestTimes, totalTime):
    """ Helper function to display the final route and time data
            Parameters:
            -----------
            bestRoutes : Pandas DataFrame
                contains the best routes that satisfy all store demands.

            bestTimes : Pandas Series
                contains the best time associated with a route permutation.

            TotalTime
                Cumulative time of all routes.

            Notes:
            ------
    """
    print(" ")
    cnt = 0
    for map in bestRoutes:
        print("Distribution Centre -->", end=" ")
        for j in range(len(map)):
            print(map[j], "-->", end=" ")
        print("Distribution Centre.", end=" ")
        print("\ttime for route:", round((bestTimes[cnt]/3600),1), "hours")
        cnt += 1

    # output of total time
    print("\ncumulative time for all regions", totalTime, "in seconds")
    print("Total cost of all routes $", 225 * totalTime / 3600 , "\n\n")

    return


def write (bestRoutes, bestTimes, totalTime, weekend):
    """ Helper function to write the final route and time data to a file for simulation
            Parameters:
            -----------
            bestRoutes : Pandas DataFrame
                contains the best routes that satisfy all store demands.

            bestTimes : Pandas Series
                contains the best time associated with a route permutation.

            TotalTime
                Cumulative time of all routes.
    """
    # create new files according to if weekend
    if weekend:
        filename = 'routes_weekend.csv'
        time = open('times_weekend.txt', 'w')
        route = open('routes_weekend.txt', 'w')
    else:
        filename = 'routes_weekday.csv'
        time = open('times_weekday.txt', 'w')
        route = open('routes_weekday.txt', 'w')


    # list of each store location
    stores = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsDemands.csv")['Store']

    # creates a zero array
    binary = np.zeros((65, len(bestRoutes)))

    # loop through each route
    for i in range(len(bestRoutes)):

        # loop through each store location
        for j in range(len(stores)):

            # current store location
            test1 = stores[j]

            # loop through stores within current route
            for k in range(len(bestRoutes[i])):

                # current store in route
                test2 = bestRoutes[i][k]

                # check to see if store location is visited
                if (test1 == test2):
                    binary[j][i] = 1

    # convert to a dataframe
    df = pd.DataFrame(binary, index=stores)

    # write to dataframe to csv file
    df.to_csv(filename)

    # loop through bestTimes
    for i in range(len(bestTimes)):
        # write time to .txt
        time.write(str(bestTimes[i]) + '\n')
    
    # This writes routes to txt
    # loop through each route
    for map in bestRoutes:
        str_r = 'Distribution Centre Auckland,'

        # loop through each store in route
        for j in range(len(map)):
            str_r += map[j] + ','

        str_r += 'Distribution Centre Auckland\n'

        # write route to .txt
        route.write(str_r,)

    route.close()

    # write total time
    time.write(str(totalTime))

    # close .txt file
    time.close()