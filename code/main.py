
from Routes import *
from Visualisations import *
from Simulation import *
import time

VehicleRoutingProblem = False
Visualisations = False # Need new ORS key
Simulation = True
# n = number of simulations
n = 10000

def VRP():

    vehicleRoutingProblem(3)
    vehicleRoutingProblem(4, True)   

def Visualise():
    
    OverallList = convertToList(weekend=False)
    regionAreas = ["North_", "City_", "East_", "SouthEast_", "South_", "West_", "NorthWest_"]

    for i in range(len(regionAreas)):
        if i == 0: weekList = OverallList[0:5]      # North
        if i == 1: weekList = OverallList[5:9]      # City
        if i == 2: weekList = OverallList[9:13]     # East
        if i == 3: weekList = OverallList[13:16]    # South East
        if i == 4: weekList = OverallList[16:20]    # South
        if i == 5: weekList = OverallList[20:24]    # West
        if i == 6: weekList = OverallList[24:]      # North West

        # visualise_region(weekList, "weekday", regionAreas[i], display_names=True)
        visualise_region(weekList, "weekday", regionAreas[i], display_names=False)
        # visualise_region(OverallList, "Weekday", "all", display_names=False)

    OverallList = convertToList(weekend=True)
    regionAreas = ["North_", "City_", "East_", "South_", "West_", "Central_"]
    for i in range(len(regionAreas)):
        if i == 0: endList = OverallList[0:3]       # North
        if i == 1: endList = OverallList[3:5]       # City
        if i == 2: endList = OverallList[5:8]       # East
        if i == 3: endList = OverallList[8:11]      # South
        if i == 4: endList = OverallList[11:14]     # West
        if i == 5: endList = OverallList[14:]       # Central

        # visualise_region(endList, "weekend", regionAreas[i], display_names=True)
        visualise_region(endList, "weekend", regionAreas[i], display_names=False)

def Simulate(n):

    #allCosts, Dropped, NotDropped = simulateRoute(n, weekend=False)  
    #summary(allCosts, Dropped, NotDropped, weekend = False)
    allCosts, Dropped, NotDropped = simulateRoute(n, weekend=True)
    summary(allCosts, Dropped, NotDropped, weekend = True)

if __name__ == "__main__":

    # record time
    start_time = time.time()

    if VehicleRoutingProblem:
        VRP()

    if Visualisations:
        Visualise()

    if Simulation:
        Simulate(n)

    print("\nExecution time --- %s seconds ---" % (time.time() - start_time))
