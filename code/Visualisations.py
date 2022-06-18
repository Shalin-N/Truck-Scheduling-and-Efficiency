import os
import folium
import openrouteservice as ors
import folium.plugins
from folium.features import *
import pandas as pd


PATHFILE = True
#set your key here
myKey = '5b3ce3597851110001cf6248909d7d69f97a48419eae393895f8b709'


# stole this from online - I have limited idea how it works but it works as needed so don't touch it
    #basically it is needed for setting the location names
class DivIcon(MacroElement):
    def __init__(self, html='', size=(30,30), anchor=(0,0), style=''):
        """TODO : docstring here"""
        super(DivIcon, self).__init__()
        self._name = 'DivIcon'
        self.size = size
        self.anchor = anchor
        self.html = html
        self.style = style

        self._template = Template(u"""
            {% macro header(this, kwargs) %}
              <style>
                .{{this.get_name()}} {
                    {{this.style}}
                    }
              </style>
            {% endmacro %}
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.divIcon({
                    className: '{{this.get_name()}}',
                    iconSize: [{{ this.size[0] }},{{ this.size[1] }}],
                    iconAnchor: [{{ this.anchor[0] }},{{ this.anchor[1] }}],
                    html : "{{this.html}}",
                    });
                {{this._parent.get_name()}}.setIcon({{this.get_name()}});
            {% endmacro %}
            """)


def visualise(route, routeName, day):
    ''' This function takes a route and visualises it on a map
        
        Parameters:
            -----------
            route : list
                list of locations in the route, in order
            routeName : string
                string that has the name of the route
            day : string - 'Saturday' or 'Week' are the only valid inputs
                the type of day that this is (which folder to save to)
    '''

    # create client and folium map
    client = ors.Client(key = myKey)
    m = folium.Map(location = [-36.95770671222872, 174.81407132219618], zoom_start=15)

    # get coords from locations csv
    coords = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsLocations.csv", index_col=2)

    # add distribution to beginning and end
    dist_routes = ('Distribution Centre Auckland',) + route + ('Distribution Centre Auckland',)
    coords_list = []
    # loop through each store in route and take co-ords
    for store in dist_routes:
        coords_list.append([coords.loc[store,'Long'], coords.loc[store,'Lat']])
    # get directions for heavy vehicles for each co-ord
    route_directions = client.directions(coordinates = coords_list, profile='driving-hgv', \
        format = 'geojson', validate = False)
    # add to map
    folium.PolyLine(locations=[list(reversed(coord))for coord in route_directions['features'][0]['geometry']['coordinates']]).add_to(m)

    # loop through each store again
    for store in dist_routes:
        # set iconCol by type for eachstore
        if coords.loc[store,'Type'] == 'Countdown':
            iconCol = "green"
        elif coords.loc[store,'Type'] == 'FreshChoice':
            iconCol = "red"
        elif coords.loc[store,'Type'] == 'SuperValue':
            iconCol = "blue"
        elif coords.loc[store,'Type'] == 'Countdown Metro':
            iconCol = "orange"
        elif coords.loc[store,'Type'] == 'Distribution Centre':
            iconCol = "black"
        # take store co-ords
        coords_store = [coords.loc[store,'Lat'],coords.loc[store,'Long']]
        # add marker for that location
        folium.Marker(coords_store, popup = coords.loc[store].name,\
            icon = folium.Icon(color = iconCol)).add_to(m)
        # add name for that location
        folium.map.Marker(coords_store,\
            icon=DivIcon(size=(150,36),anchor=(100,0),html=store,\
                style="""
                font-size:14px;
                background-color: #fff;
                border-color: white;
                text-align: right;
                """
                )
            ).add_to(m)

    #pathfile - create savename with the particular location and name
    if PATHFILE:
        savename = "code" + os.sep + "RouteMaps" + os.sep + day + os.sep + routeName + '.html'
    else:
        savename = "RouteMaps" + os.sep + day + os.sep + routeName + '.html'
    # save map
    m.save(savename)


def visualise_all_routes(bestRoutes, day):
    """This function takes a list of routes and generates maps of those routes, saving them to 'day' folder
    
        Parameters:
            -----------
            bestRoutes: List
                list of routes (as list of locations)
            day: str
                'Week' or 'Saturday'
                the type of day that we are running the program for
    """
    #loops through each route and calls visualise
    for i in range(0,len(bestRoutes)):
        visualise(bestRoutes[i], 'Route_'+str(i+1), day)


def visualise_region(routesList, day, region, display_names=False, start_coord=[-36.892506785, 174.7660359], zoom=11):
    """ This function takes a set of routes and prints them to 1 html map

            Parameters:
            -----------
            routeList : list
                a list of routes (where each route is a list of destinations)

            day : str
                what type of day it is

            region : str
                name of the region

            display_names : boolean
                whether to display the names of each location

            start_coord : array-like
                [Lat, Long] co-ordinates for center of map

            zoom : number
                start zoom level
    """
    # create client and folium map
    client = ors.Client(key=myKey)
    m = folium.Map(location=start_coord, tiles='http://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', attr='Light Gray Base', zoom_start=zoom)

    # get coords from locations csv
    coords = pd.read_csv("code" + os.sep + "data" + os.sep + "WoolworthsLocations.csv", index_col=2)

    # add marker for distribution
    folium.Marker([coords.loc['Distribution Centre Auckland', 'Lat'],
                   coords.loc['Distribution Centre Auckland', 'Long']],
                  popup=coords.loc['Distribution Centre Auckland'].name,
                  icon=folium.Icon(color="black")).add_to(m)

    # add name for distribution
    if display_names:
        folium.map.Marker([coords.loc['Distribution Centre Auckland', 'Lat'],
                           coords.loc['Distribution Centre Auckland', 'Long']],
                          icon=DivIcon(size=(140, 36),
                                       anchor=(100, 0),
                                       html='Distribution Centre Auckland',
                                       style="""font-size: 12px;
                                       background-color: rgba(204, 204, 204, 1);
                                       border-color: transparent;
                                       text-align: center;
                                       """
                                       )
                          ).add_to(m)

    cnt = 0
    RouteCol = ['red', 'green', 'blue', 'purple', 'orange', 'pink']
    # loop through routes
    for route in routesList:
        cnt = cnt % 6

        #if type(route) is str:
        #    dist_routes = ('Distribution Centre Auckland',) + (route,) + ('Distribution Centre Auckland',)
        #else:
        #    dist_routes = ('Distribution Centre Auckland',) + route + ('Distribution Centre Auckland',)

        coords_list = []



        # loop through each store in route and take co-ords
        for store in route:
            coords_list.append([coords['Long'][store], coords['Lat'][store]])

        # get directions for heavy vehicles for each co-ord
        route_directions = client.directions(coordinates = coords_list,
                                             profile='driving-hgv',
                                             format = 'geojson',
                                             validate = False)
        # add to map
        opacity = 'AA'
        red = '#ff0000' + opacity
        green = '#1EB41E' + opacity
        blue = '#0000ff' + opacity
        purple = '#9400D3' + opacity
        orange = '#FF8C00' + opacity
        pink = '#FF00FF' + opacity
        colormaps = [red, green, blue, purple, orange, pink]
        folium.PolyLine(locations=[list(reversed(coord))for coord in route_directions['features'][0]['geometry']['coordinates']],
                        color = colormaps[3]).add_to(m)

        # deals with routes of len 1 (which are otherwise interpreted as strings rather than a list as needed)
        if type(route) is str:
            route = (route,)


        for store in route[1:-1]:
            # take store co-ords
            coords_store = [coords.loc[store,'Lat'],coords.loc[store,'Long']]

            # Color by store type
            if coords.loc[store,'Type'] == 'Countdown':
                iconCol = "green"
            elif coords.loc[store,'Type'] == 'FreshChoice':
                iconCol = "red"
            elif coords.loc[store,'Type'] == 'SuperValue':
                iconCol = "blue"
            elif coords.loc[store,'Type'] == 'Countdown Metro':
                iconCol = "orange"
            elif coords.loc[store,'Type'] == 'Distribution Centre':
                iconCol = "black"

            # add marker for that location
            folium.Marker(coords_store, popup = coords.loc[store].name, icon = folium.Icon(color = iconCol)).add_to(m)

            # add name for that location
            if display_names:
                folium.map.Marker(coords_store, icon=DivIcon(size=(90, 53),
                                                             anchor=(45, 0),
                                                             html=store,
                                                             style="""font-size: 12px;
                                                             background-color: rgba(204, 204, 204, 1);
                                                             border-color: transparent;
                                                             text-align: center;
                                                             """
                                                             )
                                  ).add_to(m)

        cnt += 1

    if display_names:
        region += day + '_Routes_Labelled'
    else:
        region += day + '_Routes_Unlabelled'

    # save map
    savename = "code" + os.sep + "RouteMaps" + os.sep + "Best" + os.sep + region + '.html'
    m.save(savename)


if __name__ == "__main__":
    temp = 0

