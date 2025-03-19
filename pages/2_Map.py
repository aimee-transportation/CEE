import streamlit as st

import pyarrow.parquet as pq
import pandas as pd
import geopandas
import pyogrio
import geodatasets
import folium
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import branca.colormap as cm
import plotly.express as px

path = "./Data/totalTripsClean.csv"

st.title("Interactive Maps With Taxi and Uber Pickups")
#pulls taxi trip data and converts geometry to points
@st.cache_data
def pull_data(x):
    trips = geopandas.read_file(x)
    return trips
totalTrips = pull_data(path)

#imports NYC sub-boroughs

@st.cache_data
def pull_nycData():
    NYC = geopandas.read_file(geodatasets.get_path("geoda.nyc_neighborhoods"))
    NYC = NYC.loc[:,['boroname', 'poptot', 'medianinco','geometry', 'ntacode']]
    #changing dtyper
    NYC['medianinco'] = pd.to_numeric(NYC['medianinco'], errors='coerce')
   #adding to get correct geometric data
    NYC['uberPickups'] = totalTrips['uberPickups']
    NYC['taxiPickups'] = totalTrips['taxiPickups']
    #changing dtype again
    NYC['uberPickups'] = pd.to_numeric(NYC['uberPickups'], errors='coerce')
    NYC['taxiPickups'] = pd.to_numeric(NYC['taxiPickups'], errors='coerce')
    NYC['change'] = (((NYC['taxiPickups']-NYC['uberPickups'])*100)/(NYC['taxiPickups']))
    
    return NYC
NYC = pull_nycData()
#explain where data is from
st.header("Spatially joined taxi and uber trips with New York City sub-boroughs.")
st.write("We first cleaned the data by getting rid of any distance for taxi trips with zero values. Next we set the geometry column by using latitude and longitude values to define points. Then we spatially joined the taxi trip data with the NYC sub-borough data through a left spatial join using the within predicate. We sorted our columns by the ntacode so we could sum up the duplicated number of trips within in each sub-borough and get the total amount of trips. Finally we appended the number of taxi or uber pickups to the NYC data so we can use the polygon geometry associated with the sub-boroughs.")
NYC


m = folium.Map(location = [40.70, -73.94], zoom_start = 10)

#adding borough geometry for map layer
@st.cache_data 
def pull_nycBoro():
    nycBoro = geopandas.read_file(geodatasets.get_path("nybb"))
    return nycBoro
nycBoro = pull_nycBoro()

#yay colors

#colormap = cm.LinearColormap(
    #vmin=taxiJoin["numPickups"].quantile(0.0),
    #vmax=taxiJoin["numPickups"].quantile(1),
    #colors=["#f1eef6", "#bdc9e1", "#74a9cf", "#2b8cbe", "#045a8d"],
    #caption="Median Household Income (%)",
#)


def my_color_function(feature):
    if NYC[NYC["boroname"]] == "Bronx":
        return "#f1eef6"
    elif NYC[NYC["boroname"]] == "Brooklyn":
        return "#bdc9e1"
    elif NYC[NYC["boroname"]] == "Manhattan":
        return "#74a9cf"
    elif NYC[NYC["boroname"]] == "Queens":
        return "#2b8cbe"
    elif NYC[NYC["boroname"]] == "Staten Island":
        return "#045a8d"

#popup showing taxi data
tooltip = folium.GeoJsonTooltip(
    fields=["boroname", "medianinco", "ntacode", "taxiPickups", "uberPickups"],
    aliases=["Borough:", "2012 Median Income (USD):", "Borough Code:", "Taxi Pickups", "Uber Pickup"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)

#use add_to(m)
bcolormap = cm.linear.PuBuGn_09
#bcolormap.add_to(m)
incocolormap = cm.linear.PuBuGn_09.scale(
    NYC.medianinco.min(), NYC.medianinco.max()
)#.add_to(m)

#setting to dictionary so colormap works
taxiJoin_dict = NYC.set_index("ntacode")["medianinco"]

#creating three main layers below, median inco, taxi trips, change in num trips


folium.Choropleth(
    geo_data = NYC.geometry,
    data = NYC,
    columns = [NYC.index, 'medianinco'],
    key_on = 'feature.id',
    name = "2012 Median Income",
    fill_color="YlOrBr",
).add_to(m)

# for i in taxiJoin_dict.keys():
#     st.write(taxiJoin_dict[i])

folium.GeoJson(
    NYC,
    name = "Toal Trips",
    style_function=lambda x: {
        #mediancolormap(taxiJoin_dict.all()),
        "color": "black",
        "fillOpacity": 0,
    },
    tooltip = tooltip
).add_to(m)

#toggable layer
folium.LayerControl().add_to(m)
st.header("2012 Median Income Interactive Map")
st.write("Use your mouse below to hover over each sub-borough to see the number of taxi or uber pickups associated with the median income of that area.")
output = st_folium(m, width = 700, height = 500)

#yay colors that work
st.header("Heatmap for Taxi Pickups")

figtaxi = px.choropleth(NYC, geojson=NYC.geometry, locations=NYC.index,
                    color='taxiPickups', color_continuous_scale="oryel",
                    projection="mercator")
figtaxi.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(figtaxi)

st.header("Chart Highlighting Difference Between Taxi and Uber Pickups")
figchange = px.choropleth(NYC, geojson=NYC.geometry, locations=NYC.index,
                    color='change', color_continuous_scale="oryel",
                    projection="mercator")
figchange.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(figchange)


st.header("Table Highlighting Difference Between Taxi and Uber Pickups")
st.write("Let's look at the negative values for the percent change. This means that there were more uber pickups than taxi pickups in that sub-borough. While the higher number of ubers may decrease some taxi activity, overall taxi pickups remain the dominant form of transportation in NYC. Looking at the negative numbers shows that uber pickups may have increased accessibility to ride sharing options for sub-boroughs in Brooklyn and the Bronx.")
NYC = NYC.sort_values(by=['change'], ascending = True)
NYC.loc[:,['boroname','ntacode', 'change']]

