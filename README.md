# OR-Project-Team8

ENGSCI 263 OR project; team 8

Woolworths NZ would like us to determine a suitable truck logistics plan, such that costs are minimised. They have provided us with: 

### Given
- **WoolworthsDemands.csv**         : Number of pallets delivered to each store they operate over a 4 week period (pre-lockdown), 
- **WoolworthsDistances.csv**       : Road distance (in meters) between each pair of stores and distribution points. 
- **WoolworthsLocations.csv**       : GPS coordinate of each store and the distribution centre
- **WoolworthsTravelDurations.csv** : Travel durations (in seconds) between each pair of stores and distribution points.

- Each truck can carry up to 26 pallets of goods.
- A pallet takes on average 7.5 minutes to unload.
- Each scheduled trip take no more than four hours, on average.
- Each truck costs $225 per hour to operate.
- Each truck can operate two (approximately) four-hour shifts per day.
- Two shifts start at 8am or 2pm.
- Each store only receives one delivery per day.
- Extra time costs Woolworths $275 per hour.
- Additional trucks can be ‘wet-leased’ for a cost of $2000 for every four hours of on-duty time, charged in four-hour blocks.
  
### Assume
- Times between stores are unidirectional.
- Demand of each weekday is averaged to find one mean value.

### Notes
 - You will need to insert your personal key to use route_visual

### Functions
 - Routes.py
 - generate_demands.py
 - route_visual.py
 - main.py
 - unit_tests.py
 - routeSizeVis.py
 