import numpy as np
import pandas as pd
import os


PATHFILE = True

def demandEstimation1(type = 'Ceil', Saturday = False):
    ''' This generates demands for each from the demand data, either in the form random, average or average
        rounded up. It can generate for the week, or for Saturdays
    
        Parameters:
        -----------
        type : string
            string with the label of the type of generation we want - either 'Ceil', 'Mean' or 'Random'
            default set to 'Ceil'
        Saturday : Boolean
            Boolean reflecting whether we want to generate demand for Saturday (else we generate for the weekdays)
            False by default

        Returns:
        --------
        demand : dataframe column
            dataframe column with the generated demand for each location
        
    '''


    if PATHFILE:
        initial = pd.read_csv("code" + os.sep + "data" + os.sep + "DemandLongPivot.csv", index_col=0)
    else:
        initial = pd.read_csv("data" + os.sep + "DemandLongPivot.csv", index_col=0)

    # Set index for the dataframe to be 'Store'
    initial.set_index('Store')

    # Generate demand based on Saturday demand or not
    if Saturday == True:
        # take all the data from days that are saturday
        weekend = initial[initial['day']=='Saturday']
        # pivot so that there is a column for each date
        pivoted = weekend.pivot(index = 'Store', columns = 'date', values = 'demand')
        # take the mean of each row (ie each store)
        mean = pivoted.mean(axis = 1)
        # take the ceiling of the means
        ceil_mean = mean.apply(np.ceil)
        # find the standard deviation of each row (ie each store)
        std = pivoted.std(axis = 1)
        # generate a dictionary with the mean, ceiling and std
        frame = { 'Mean': mean, 'Ceil Mean': ceil_mean, 'Deviation' : std}
        # turn this dictionary into a dataframe
        all_data = pd.DataFrame(frame)
    else:
        # take all the data from days that are weekdays
        weekday = initial[initial['day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
        # pivot so that there is a column for each date
        pivoted = weekday.pivot(index = 'Store', columns = 'date', values = 'demand')
        # take the mean of each row (ie each store)
        mean = pivoted.mean(axis = 1)
        # take the ceiling of the means
        ceil_mean = mean.apply(np.ceil)
        # find the standard deviation of each row (ie each store)
        std = pivoted.std(axis = 1)
        # generate a dictionary with the mean, ceiling and std
        frame = { 'Mean': mean, 'Ceil Mean': ceil_mean, 'Deviation' : std}
        # turn this dictionary into a dataframe
        all_data = pd.DataFrame(frame)

    # Return data based on what type we want (ceil, mean or random)
    if type == 'Ceil':
        return all_data['Ceil Mean']
    elif type == 'Mean':
        return all_data['Mean']
    else:
        random = []
        # Loop through each store and generate a random normal value with the mean and deviation we have found for this store
        for store in all_data.index:
            random.append(np.random.normal(all_data['Mean'][store], all_data['Deviation'][store], 1)[0])

    all_data['Random'] = random
    return all_data['Random']


def demandEstimation2():
    ''' Creates a csv that estimates the average pallet demands at each store for weekdays and saturday

        Notes
        -----


    '''
    if PATHFILE:
        demands = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsDemands.csv", index_col=0)
    else:
        demands = pd.read_csv("data" + os.sep + "WoolworthsDemands.csv", index_col=0)

    weekDemands = []
    saturdayDemands = []

    # loop through row
    for i in demands.index:

        # new demands and cnt for each store
        weekTemp = 0
        saturdayTemp = 0
        cnt = 2

        # loop through columns
        for j in demands.columns:

            # check for saturday
            if (cnt) % 7 == 0:
                saturdayTemp += demands[j][i]
            else:
                weekTemp += demands[j][i]

            cnt += 1

        # averages per store
        weekTemp = weekTemp / 20
        saturdayTemp = saturdayTemp / 4

        # append for each store
        weekDemands.append(weekTemp)
        saturdayDemands.append(saturdayTemp)

    # rounding to whole numbers
    weekDemands = np.ceil(weekDemands)
    saturdayDemands = np.ceil(saturdayDemands)

    # convert to dataframe to store in csv
    zero = pd.Series(weekDemands, index=demands.index)
    one = pd.Series(saturdayDemands, index=demands.index)
    df = pd.DataFrame({'0': zero, '1': one})

    # write to csv
    if PATHFILE:
        df.to_csv('code' + os.sep + 'data' +os.sep +'DemandEstimation.csv')
    else:
        df.to_csv('data' +os.sep +'DemandEstimation.csv')

def demandEstimation3(initial, type = 'Ceil', Saturday = False):
    ''' This generates demands for each from the demand data, either in the form random, average or average
        rounded up. It can generate for the week, or for Saturdays
    
        Parameters:
        -----------
        type : string
            string with the label of the type of generation we want - either 'Ceil', 'Mean' or 'Random'
            default set to 'Ceil'
        Saturday : Boolean
            Boolean reflecting whether we want to generate demand for Saturday (else we generate for the weekdays)
            False by default

        Returns:
        --------
        demand : dataframe column
            dataframe column with the generated demand for each location
        
    '''

    # Set index for the dataframe to be 'Store'
    initial.set_index('Store')

    # Generate demand based on Saturday demand or not
    if Saturday == True:
        # take all the data from days that are saturday
        weekend = initial[initial['day']=='Saturday']
        # pivot so that there is a column for each date
        pivoted = weekend.pivot(index = 'Store', columns = 'date', values = 'demand')
        # take the mean of each row (ie each store)
    else:
        # take all the data from days that are weekdays
        weekday = initial[initial['day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
        # pivot so that there is a column for each date
        pivoted = weekday.pivot(index = 'Store', columns = 'date', values = 'demand')
    # take the mean of each row (ie each store)
    mean = pivoted.mean(axis = 1)
    # take the ceiling of the means
    ceil_mean = mean.apply(np.ceil)
    new = pivoted.sub(mean, axis='index')
    standard = new.stack().std()
    # generate a dictionary with the mean, ceiling and std
    frame = { 'Mean': mean, 'Ceil Mean': ceil_mean}
    # turn this dictionary into a dataframe
    all_data = pd.DataFrame(frame)

    # Return data based on what type we want (ceil, mean or random)
    if type == 'Ceil':
        return all_data['Ceil Mean']
    elif type == 'Mean':
        return all_data['Mean']
    else:
        random = []
        # Loop through each store and generate a random normal value with the mean and deviation we have found for this store
        for store in all_data.index:
            value = np.round(np.random.normal(all_data['Mean'][store], standard, 1)[0])
            if value > 0:
                random.append(value)
            else:
                random.append(0)

    all_data['Random'] = random
    return all_data['Random']

if __name__ == "__main__":
    df = demandEstimation3(type = 'Random', Saturday=False)
    print(3)
    #demandEstimation2()