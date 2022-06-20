# To Do
- clean up directory
- fix comments in simulation code

# Executive Summary

### Goals
Within this report, we aim to assist Woolworths New Zealand in creating a cost-efficient routing plan that is stable for the uncertainty of traffic and store demand, and make recommendations for the future operation of stores and trucks that belong to their branch.

### Approach
1.	Analyse the given data to estimate the demand per store
2.	Split the stores into geographical regions 
3.	Generate routes for a fixed demand estimation
4.	Solve routes for the best routing plan using an integer linear program
5.	Run best routes through 1000 simulations, testing their stability for varying travel time and store demand.
6.	Make recommendations depending on the outcome of the simulation

### Findings
For weekdays, we simulated the cost of $21,390 with 95% confidence intervals of $21,086 to $21,764. For Saturday, we simulated the cost of $10,633 with 95% confidence intervals of $10,468 to $10,796. During weekdays two routes broke 30% of the time in 1000 simulations, and for weekends no routes broke. 

### Recommendations
I recommended that two stores should be merged due to being within 500m of another store. Further store closure should be avoided to the broader impact they have. Our recommendations and model are only accurate for our data. There is no guarantee that given different sample data, our predictions would still hold.

# Introduction
There is an uncertainty with demand across Woolworths chains store each day. If the store is unable to meet its demand, it affects the image and profits of Woolworths New Zealand and the lively hood of the public. In this report, we aim to provide a cost-efficient routing plan that can account for this randomness. The company has a fleet of 30 vehicles with 26 pallet capacity that needs to satisfy the demand at each store each day. Each vehicle follows a route that starts at the distribution centre, visits some stores, and returns to the distribution centre. We assume that the total demand of a store must be carried by one vehicle and cannot be met by several trucks. It is also of interest to find stores that are unusually close to each other due to historical lease agreements and make recommendations on their future operation. 

# Methods
Our method consisted of 3 parts. First, we explored the data given to understand each store's profiles better and find common trends. Second, we generated a fixed routing plan using combinatorics and scheduling for a fixed demand estimation at each store. Thirdly, we simulated our routing plan against realistic varying demands to see whether it was stable and determine the uncertainty in cost. 

## Data Analysis
### Demand Estimation
We explored the demand profile for each store to make a reasonable estimate of the average demand at each store which would later be used to generate our routes. The estimations can be found in Appendix A.

![image](https://user-images.githubusercontent.com/85419997/174465392-0cfc4e59-1b64-43d9-a9d3-e753dcaff148.png)
<br><i>Figure 1: Plot of average demand for supermarket types: Countdown, Countdown Metro, Fresh Choice and SuperValue</i>

We found that the Countdown store type has roughly twice the demand of all other stores on average. In addition, on Saturdays, the Countdown store type has half their usual demand on average, and all other store types have 0 demand. On Sundays, all stores have 0 demand. Also of interest was that the Countdown Metro store type had the largest variation in demand.

Since the demand across the weekdays had a relatively small deviation and Saturdays had a large deviation, we treated Saturdays differently in our solution. We decided to solve the problem twice, one set of routes for weekday conditions and another set of routes for Saturday conditions. Sunday could be ignored  as there was 0 demand on this day.

### Regions
We grouped each store into 1 of x geographical regions. 
Where x is [North, City, East, SouthEast, South, West, NorthWest] on weekdays, 
or x is [North, City, East, South, Central, West] on Saturday. 

This was done to simplify the overall linear program, under the assumption that no (or very few) optimal routes would cross the regional borders as we defined. This was done by inspection, creating division by geographical groupings. 

![image](https://user-images.githubusercontent.com/85419997/174465472-ac02f30b-a288-4c96-ba09-65b06cd824a5.png)
<br><i>Figure 2: Region Allocation for all store types, Weekday (Left) and Weekend (Right)</i>

For weekdays each region had either 9 or 10 stores, which allows for good groupings which can be seen in <b>Figure 2</b>. Because many stores had 0 demand on Saturdays, we generated a different set of regions (and thus routes) for Saturdays. Here we split the stores into 6 regions ranging from 9 to 11 stores per region.

## Route Generation
### Route Combinations
Using combinatorics, we created every possible combination of stores up to a maximum of 4 per region. Feasible routes where the total demand of all stores exceeded 26 were ignored.

For weekdays we found that:
No length 4 routes were used in our optimal routing solution, so to improve the computational efficiency of our algorithm, we limited it to routes of length 3 or less.

However, for weekends, we found that:
generating routes of up to length 3, only increased the optimal cost by roughly 500 dollars and significantly improved the algorithm's execution time.

Using length 3 for weekends should be considered in a situation with more stores due to the shorter computation time. However, since our program was still computationally cheap using routes of length 4, we chose to continue with this.

A maximum cluster size of 5 was also considered but ultimately ignored. We found that only 6% of length-5 routes were valid for weekdays, as opposed to 37% for length-4 routes. The increase in computational cost from simulating clusters of size 5 far outweighed the increase in quality of our solution.

We found that the odds of a length 5 route being valid for the Saturday demand were about 90%. However, considering the size of regions, the computational cost of including length-5 routes was a massive increase. The other option would have been smaller regions (6 regions of 8 or 9), but with regions this small, length-5 routes are pointless (A length 5 and a length 3 route or 2 length 4 routes both take 2 trucks to satisfy). 

### Permutations
Using our generated combinations, I created permutations of each route to calculate the shortest (in time) tour. The maximum permutation size was 4! (24), which was computationally cheap. The distribution centre was added to the start and end of each tour and then each permutation was costed, including the 7.5-minute unloading time per pallet per store. The shortest permutation was saved. Once we had calculated the shortest permutation if it exceeded 4 hours, it was ignored in the linear program.

### Linear Program
To create our routing plan, I took all our generated routes and their associated best permutation and solved them in scheduling an integer linear program for a fixed demand. This is a vehicle routing problem which is an extension of the well-known travelling salesman problem. Given that it's parameters were not enumerated it will not provide the most optimal solution, but it will provide a solution of similar quality

![image](https://user-images.githubusercontent.com/85419997/174465582-b172ce4d-60df-43db-99de-c3a89931b685.png)

## Simulation
### Route Simulation
Using the deterministic routes solved for fixed demands, we simulated if our routes were feasible for random demands and random traffic conditions. If routes were not feasible the store closest to the distribution centre in the current route was dropped and added to a list that would later be used to create a route so that the stores' demand was still met. 

### Traffic Estimation
According to a study published in the Journal of Modern Transportation, the lognormal distribution is best used to describe traffic variation.
Based on the traffic observations made in Auckland. We calibrated the lognormal distribution. ln⁡(traffic)~ (N(μ,σ^2 )-C )* K.  Where μ=2.3, σ=0.5,C=8,K=0.8

### Store Demand Estimation
For each store in the route the demands per simulation was randomly generated according to a normal distribution.  The normal distribution was fitted to the demand data we were given.

### Store Merger
I estimated that the expected new demand due to a store merger can be estimated by:
MergeDemand = CEIL [(Store1Demand + Store2Demand)*90%]

This assumes that:
- Each store has 1 pallet of food waste per day due to overstocking.
- Thus when 2 stores merge the new overstocking value is less than the 2 original stores combined.

# Results
## Route Generation
As discussed, we solved Weekdays and Weekends independently, with routes up to length four for weekends and length three for weekdays. For visualisations of our routes refer to Appendix B. Our results yielded:

<b>Weekdays</b>
- The total cost of delivering to all stores was $20,971.27. 
- Using 28 trucks in total, were no route exceeded 4 hours. 
-	This solution was generated using routes of up to length 3.

<b>Weekends</b>
-	The total cost of delivering to all stores was $10,483.44. 
-	Using 16 trucks in total, were no route exceeded 4 hours.
-	This solution was generated using routes of up to length 4.

We assumed that truck rental is billed to the second. Travel time was kept in seconds throughout and converted to after the final calculation. Another assumption we may wish to explore is the cost of billing to the minute. This would increase the total cost by a maximum of $105 dollars.

## Simulation
![image](https://user-images.githubusercontent.com/85419997/174465651-f2854117-937f-436a-9027-07d4e506ef1f.png)
<br><i>Figure 3 Density histogram of 1000 simulated costs for Monday to Friday</i>

![image](https://user-images.githubusercontent.com/85419997/174465658-e408b237-57f9-4e5b-b6d7-ac7658da5dd2.png)
<br><i>Figure 4 Table of dropped stores for 1000 simulations from Monday to Friday</i>

For weekdays we simulated that on average the cost will be $21,390 
with 95% confidence intervals of $21,086 to $21,764.

The routes including Countdown Papatoetoe and Onehunga were of interest as they often exceeded the demand limit. Roughly 30% of the time they needed to be split further. The variance of cost reflected this but was still a small increase comparatively.

The distribution of costs looks normally distributed with a slight right skew. This is logical because the loading times have a greater impact than travel times. The travel time only adds a slight skew to the overall distribution.

![image](https://user-images.githubusercontent.com/85419997/174465666-dacb100c-e636-4400-8327-18f3a04462f0.png)
<br><i>Figure 5 Density histogram of 1000 simulated costs for Saturday</i>

In our simulations for Saturday routes, the demand never exceeded 26 pallets per truck. This led to a very consistent distribution of costs because the routes did not vary, and the difference in cost came down to the randomness in travel times.

We simulated that on average the cost will be $10,633 with 
95% confidence intervals of $10,468 to $10,796.

# Conclusion
We generated an optimal cost routing plan for weekdays and Saturdays where an estimate of average demand per store was used. This was achieved using combinatorics and permutations. Our deterministic routes were then simulated to check whether said routing plan would be stable for the random conditions induced by the uncertainty of everyday life. Our Generated routes were simulated 1000 times and the result were that 2 routes tended to break 30% of the time.

## Recommendations
I would recommend that the stores:
1.	Countdown Aviemore Drive & Countdown Highland Park should be merged.
2.	Countdown Northwest & Countdown Westgate should be merged.

For both recommendations the stores are within 500m of each other. We can expect the new demand at our merged stores to be:
1.	16 pallets per day during the week & 7 pallets per day on Saturday
2.	16 pallets per day during the week & 9 pallets per day on Saturday

This store merger does not affect have a substantial effect on the routing plan and makes it more stable as the new merged store demand is less than the previous. The saving in time will almost be negligible as both stores are situated within 500m of each other (Appendix C). There is also no need to invest in additional trucks as the current routing plans is efficient enough to not use all 30 trucks for any given day.

## Discussion
I could have recommended closing more stores, but there are wider implications such as job loss and the negative image that it conveys towards the brand. That is why I suggested a merger of only 2 stores that were abnormally close to each other as it achieves similar goals but has a less negative impact.

One of the drawbacks of our model is that it is based on a fixed set of routes. A more robust model would resolve the routing problem for changing demands each day. Our simulation also doesn't consider the traffic variation due to the time of day. A more robust simulation would assume longer travel times during the morning due to work traffic. 

Our model is only accurate for our data, and there is no guarantee that given different sample data, it would hold together. We tried to account for this by using simulation, but this is still, at best, an approximation and may not reflect real conditions.  

# Appendix A
![image](https://user-images.githubusercontent.com/85419997/174465742-3ab18a4f-6120-4e44-9112-01a92822b637.png)

# Appendix B
## Weekday
![image](https://user-images.githubusercontent.com/85419997/174465752-0ffdd6cd-f2ef-4b2b-b869-589b9b4bf563.png)
![image](https://user-images.githubusercontent.com/85419997/174465769-acb93ecf-7e69-4550-8700-6d18a1e6e082.png)

## Saturday
![image](https://user-images.githubusercontent.com/85419997/174465776-c209b9e0-d76a-4b3e-a678-e9f30805fd8f.png)
![image](https://user-images.githubusercontent.com/85419997/174465823-88a53285-a4a5-44bc-ad64-cbd9ece7129b.png)

# Appendix C
![image](https://user-images.githubusercontent.com/85419997/174465837-3f28ae4d-f688-4a93-947b-918e524f8d72.png)
![image](https://user-images.githubusercontent.com/85419997/174465840-4f452768-8cb9-47c8-9a3f-73b45c796518.png)


