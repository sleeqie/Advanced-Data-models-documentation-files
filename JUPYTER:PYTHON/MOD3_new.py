#!/usr/bin/env python
# coding: utf-8

# ## Cloud computing using Jupyter
# ## MOD3- Advances Data analysis
# ### Dr. Nanki Sidhu 
#  Parts of this code is adapted from work by Tyler Erikson, developer of GEE

# ### Start with installing all the necessary libraries 
# ### The following are important - ipyleaflet, ee, geemap, numpy (version 1.19.3)

# In[ ]:


get_ipython().system('pip install ipyleaflet ')
# Leaflet library for creating interactive visualizations


# In[ ]:


get_ipython().system('pip install --user numpy==1.19.3')
# Use this to override a bug with the latest version of Numpy library


# In[ ]:


get_ipython().system('pip install --user geemap')
# Installing a python library for connectivity to GEE


# ### After installation, we use the command "import" to initialize them

# In[ ]:


import geemap 
#Import the library


# In[ ]:


import ipyleaflet


# In[ ]:


import ee


# In[ ]:


from ipyleaflet import Map, basemaps, basemap_to_tiles, FullScreenControl, Marker
import ipyleaflet
import ipywidgets
import ipywidgets as widgets
from IPython.display import display, clear_output
# Importing some libraries that help with creating widgets such as basemaps, zoom levels, markers, etc.


# ### In order to proceed, we now will access our Google Earth Engine accounts through Jupyter. 
# 
# #### First step is to authenticate our accounts, followed by initialization. 
# ##### Aunthentication only needs to be done the first time, initialization must be done every time you run a script.

# In[ ]:


ee.Authenticate() 
# You only need to do this the first time accessing GEE from python. After running this command, you will be redirected 
# to Google where you can authenticate your account and a code will be generated that you can paste below. 


# In[ ]:


ee.Initialize()
# Initialize the GEE environment


# # Example 1: Accessing dataset from the European Centre for Medium-Range Weather Forecasts (ECMWF). 
# 
# ## GEE has a very user friendly environment and you can always access the homepage to get more detailed information on the datasets.
# 
# ## Steps
# 
# * Lets select a dataset to work with - In our case, the ECMWF Monthly global weather data
# * Lets select one specific variable to plot. For example, Mean air Temperature
# * Using the geemap library, lets plot this map.
# *  We can set different parametres such as the size of the plot, assign specific colors or a predefined color map to depict different values, set the minimum and maximum values to be displayed. 
# 

# In[ ]:


img_test = ee.Image('ECMWF/ERA5/MONTHLY/200001')


# In[ ]:


t2m = img_test.select('mean_2m_air_temperature') # Select only one variable, air temperature


# In[ ]:


Map = geemap.Map(zoom=2,
                layout={'height':'1000px'})
t2m_palette=['#000080','#0000D9','#4000FF','#8000FF','#0080FF','#00FFFF','#00FF80','#80FF00','#DAFF00','#FFFF00','#FFF500','#FFDA00','#FFB000','#FFA400','#FF4F00','#FF2500','#FF0A00','#FF00FF']
Map.addLayer(t2m, {'min': 250, 'max': 330, 'palette':t2m_palette})
Map


# # Example 2: Create a static map
# 
# ## Lets load an image from Landsat 8 collection. You can find the information about the collection under 'datasets' on the GEE homepage. 
# 
# The Data Description page contains the Image ID value LANDSAT/LC08/C01/T1_SR, a key piece of information that we will use in our Python code to refer to the asset.

# In[ ]:


import bqplot
import datetime
import dateutil.parser
import ipywidgets
import IPython.display
import pprint
import pandas as pd
import traitlets

# Configure the pretty printing output.
pp = pprint.PrettyPrinter(depth=4)


# In[ ]:


l8sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') #Access the image collection from the GEE catalogue


# In[ ]:


sample_image = ee.Image(
    l8sr.filterDate('2017-11-01', '2017-12-02')
        .filterBounds(ee.Geometry.Point(-73.9957, 40.7262))
        .first()
)

band_names_original = sample_image.bandNames()
band_names_original.getInfo()


# **Rename the Bandnames for us to remember them easier**
# 

# In[ ]:


l8_bands = ee.Dictionary({
    'B1':'ultra_blue',
    'B2':'blue',
    'B3':'green',
    'B4':'red',
    'B5':'nir',
    'B6':'swir_1',
    'B7':'swir_2',
    'B8':'pan',
    'B9':'cirrus',
    'B10':'tirs_1',
    'B11':'tirs_2',
    'sr_aerosol':'sr_aerosol',
    'pixel_qa':'pixel_qa',
    'radsat_qa':'radsat_qa'
})
bandnames_new = l8_bands.values(sample_image.bandNames())
l8sr = l8sr.select(band_names_original, bandnames_new)


# **Print the metadata for our sample image**

# In[ ]:


sample_image = ee.Image(
    l8sr.filterDate('2017-11-10', '2017-12-01')
        .filterBounds(ee.Geometry.Point(-73.9957, 40.7262))
        .first()
)
#You can change the above parametres, such as filter for dates or location. 
#first() brings the first image in an image collection

pp.pprint(sample_image.getInfo())


# **We can create a thumbnail of the image, and generate a URL for it.**

# In[ ]:


url = sample_image.getThumbUrl({'min':0, 'max':3000, 'dimensions': 600})
print(url)


# **OR**

# In[ ]:


thumbnail = sample_image.getThumbUrl({'bands':'red,green,blue',
                                      'min': 0 ,
                                      'max': 3000 ,
                                      'region': sample_image.geometry().bounds().getInfo(),
                                       'dimensions': 600})
IPython.display.HTML('Thumbnail URL: <a href={0}>{0}</a>'.format(thumbnail))


# # Example 3: Create an interactive map
# 
# The iPyLeaflet library can be used to generate interactive maps.

# In[ ]:


# Draw a basic OpenStreetMap basemap layer.
map1 = ipyleaflet.Map(zoom=3, layout={'height':'400px'})
dc = ipyleaflet.DrawControl() #Allows you to draw shapes on the map
map1.add_control(dc)
map1


# **To display an Earth Engine generated image on the interactive map, we can use ipyleaflet's TileLayer object.**
# 
# First we start by defining a function that can generate a tile layer URL from an Earth Engine image object.

# In[ ]:


def GetTileLayerUrl(ee_image_object):
  map_id = ee.Image(ee_image_object).getMapId()
  tile_fetcher = map_id['tile_fetcher']
  return tile_fetcher.url_format


# Now we will select an image collection that we want to work with. For the purpose of this example, we will use Sentinel 2 image collection. You can find more data on the collection under datasets on GEE. 

# In[ ]:


s2 = ee.ImageCollection('COPERNICUS/S2_SR')


# In[ ]:


# We want one image from our collection
sample_image2= ee.Image(
        s2.filterDate('2020-11-01', '2020-11-11')
        .filterBounds(ee.Geometry.Point(37.505523, -1.874832))
        .first()
)

#Filtered to one day


# We then can create a tile layer that displays the Sentinel-2 data, and add it to the map.

# In[ ]:


sentinel2_tilelayer = ipyleaflet.TileLayer(
   name='Sentinel 2',
   url=GetTileLayerUrl(
       sample_image2.visualize(
           min=0,
           max=3000,
           gamma=1.5,
           bands= ['B4', 'B3', 'B2']
       )
   ),
   attribution='Map tiles by <a href="http://earthengine.google.com/">Earth Engine</a>.'
)
map1.add_layer(sentinel2_tilelayer)


# We can also add a layer control to our map, the will allow us to toggle the visibility of layers.

# In[ ]:


# Adding the layers control to the map.
map1.add_control(ipyleaflet.LayersControl())


# The preceding code block did add a layer to a map, but it is a little cumbersome to see because the map was displayed earlier in the notebook and may now be off the screen. If we want, we can display the map in the notebook a second time...

# In[ ]:


map1


# # Example 4 : Playing with python widgets and creating climate graphs ( A bit more advanced) 
# 
# 
# Adapted from Julia Wagemann notebooks (Github - JWagemann)

# In[ ]:


# We need the following libraries - Plotly, iPyleaflet and Widgets 
get_ipython().system('pip install plotly ')


# In[ ]:


get_ipython().system(' pip install chart_studio')


# In[ ]:


from ipyleaflet import Map, basemaps, basemap_to_tiles, FullScreenControl, Marker
import ipyleaflet

from IPython.display import display, clear_output
import ipywidgets as widgets
import numpy as np
import ee

import chart_studio.plotly as py
import plotly.offline as py
import plotly.graph_objs as go


# In[ ]:


# Lets start once again with the collection from example 1

era5_monthly = ee.ImageCollection('ECMWF/ERA5/MONTHLY')


# In[ ]:


era5_monthly.getInfo() #metadata check 


# In[ ]:


# Def Tile function exactly as in Example 3

def GetTileLayerUrl(ee_image_object):
  map_id = ee.Image(ee_image_object).getMapId()
  tile_fetcher = map_id['tile_fetcher']
  return tile_fetcher.url_format


# ### We want to plot mean precipitation for each month of the time series 

# In[ ]:


era5_monthly_img = era5_monthly.limit(1).first() # We pick the first image of the each month
collection_img_proj = era5_monthly_img.select(0).projection()


# In[ ]:


months = range(1,13)

# Store images in a list
img_list = []
for i in months:
    collection_filtered = era5_monthly.filter(ee.Filter.calendarRange(i,i, 'month'))
    collection_red = collection_filtered.reduce(ee.Reducer.mean())
    
    # if reducer function is applied to an image collection, the output does not have any projection information, as collection can contain \ 
    # images with different projection information. Thus, one can set the projection to each image
    collection_red_proj = collection_red.setDefaultProjection(collection_img_proj)
    img_list.append(collection_red_proj)
    
#img_list[0].getInfo()


# In[ ]:


# Build a new collection from our selected images 
meanMonths_collection = ee.ImageCollection.fromImages(img_list)
#meanMonths_collection.getInfo()


# In[ ]:


t2m_tmp = meanMonths_collection.select('mean_2m_air_temperature_mean').first()
tp_tmp = meanMonths_collection.select('total_precipitation_mean').first()


# In[ ]:


# Our map parametres for both our image instances that we want to plot 

img_t2m = GetTileLayerUrl(t2m_tmp.visualize(min=250, max=330, palette=['#000080','#0000D9','#4000FF','#8000FF','#0080FF','#00FFFF','#00FF80','#80FF00','#DAFF00','#FFFF00','#FFF500','#FFDA00','#FFB000','#FFA400','#FF4F00','#FF2500','#FF0A00','#FF00FF']))
img_tp = GetTileLayerUrl(tp_tmp.visualize(min=0, max=1, palette=['#FFFFFF', '#00FFFF', '#0080FF', '#DA00FF', '#FFA400','#FF0000']))


# In[ ]:


## Lets build our plots, these are controls for every little element of our final graphs!

def click(b):
    point = ee.Geometry.Point(lon,lat)
    tp_point = meanMonths_collection.select('total_precipitation_mean').getRegion(point,500).getInfo()
    t2m_point = meanMonths_collection.select('maximum_2m_air_temperature_mean').getRegion(point,500).getInfo()
        
    header_tp = tp_point[0]
    data_tp = tp_point[1:]
    ydata_tp = [row[4]*1000 for row in data_tp]
    
    header_t2m = t2m_point[0]
    data_t2m = t2m_point[1:]
    ydata_t2m = [row[4]-273.2 for row in data_t2m]

    tp = go.Bar(
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=ydata_tp,
        name='Total precipitation in mm',
        marker=dict(
            color='rgb(204,204,204)',
        ))
    
    t2m = go.Scatter(
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=ydata_t2m,
        name="2m air temperature in deg C",
        yaxis='y2')

    data = [tp,t2m]
    layout = go.Layout(
        title='Climate graph at location '+ str(round(lat,2)) + ' / '+ str(round(lon,2)) + ' (lat/lon)',
        yaxis=dict(
            title="Total precipitation in mm"
        ),
        yaxis2=dict(
            title="2 m air temperature in degC",
            overlaying='y',
            side='right',
            range=[0,max(ydata_t2m)+2]
        )
    )

    fig = go.Figure(data=data, layout=layout)
    with out:
        clear_output(wait=True)
        display(py.iplot(fig,filename='test'))


# In[ ]:


map2 = ipyleaflet.Map(
    zoom=2,
    layout={'height':'500px'},
)

map2.add_layer(ipyleaflet.TileLayer(url=img_t2m))
map2.add_layer(ipyleaflet.TileLayer(url=img_tp))
map2.add_control(ipyleaflet.LayersControl())

control = FullScreenControl()
map2.add_control(control)

map2


# In[ ]:


def handle_click(**kwargs):
    if kwargs.get('type') == 'click':
        global lat, lon
        mark = ipyleaflet.Marker(location=kwargs.get('coordinates'))
        map2.add_layer(mark)
        location = mark.location
        lat, lon = location[0], location[1]        

map2.on_interaction(handle_click)


# In[ ]:


out=widgets.Output()
button=widgets.Button(description='Plot climate graph')
button.on_click(click)
display(out)
display(button)


# In[ ]:




