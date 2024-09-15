"""
This script contains functions to load and preprocess all necessary datasets from dhakar in Bangladesh (data from API).
"""



# 1. Rainfall Data
# Source: Bangladesh Meteorological Department (BMD)
# Dataset: Historical daily rainfall data for Dhaka over the past 20 years
# Format: CSV
# Access Method:
# Visit the BMD website and look for the data archive or contact them directly to request the data.
# Alternatively, if direct data access is not possible, consider using global datasets like CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data) or CRU TS (Climatic Research Unit gridded Time Series).
# Python Code to Download CHIRPS Data:


import cdsapi

c = cdsapi.Client()

# Define the parameters for CHIRPS data
c.retrieve(
    'satellite-chirps-daily',
    {
        'format': 'netcdf',
        'variable': 'precipitation',
        'area': [
            23.95, 90.2, 23.6, 90.55,
        ],  # North, West, South, East
        'date': '2000-01-01/2020-12-31',
    },
    'data/dhaka_rainfall.nc')


# 2. Elevation Data
# Source: Shuttle Radar Topography Mission (SRTM)
# Dataset: Digital Elevation Model (DEM) of Dhaka
# Format: GeoTIFF
# Access Method:
# Download from the USGS EarthExplorer website. You'll need to create an account.
# Python Code to Download SRTM Data:
# Using the elevation library:

import elevation

# Define the bounding box for Dhaka
bounds = (90.2, 23.6, 90.55, 23.95)  # (west, south, east, north)

# Download and clip the SRTM data
elevation.clip(bounds=bounds, output='data/dhaka_dem.tif')



# 3. Land Use Data
# Source: OpenStreetMap
# Dataset: Land use and land cover data for Dhaka
# Format: Shapefile or GeoJSON
# Access Method:
# Use the Overpass API to query and download land use data.
# Alternatively, download pre-packaged data from Geofabrik.
# Python Code to Download Land Use Data via Overpass API:


import overpy
import geopandas as gpd
from shapely.geometry import Polygon

api = overpy.Overpass()
# Define the bounding box
bbox = (23.6, 90.2, 23.95, 90.55)  # (south, west, north, east)

# Overpass QL query
query = f"""
[out:json];
(
way["landuse"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
);
out body;
>;
out skel qt;
"""

result = api.query(query)

# Process the data
# ... [Code to convert result to GeoDataFrame] ...


# 4. Drainage Infrastructure Data
# Source: Dhaka Water Supply and Sewerage Authority (DWASA) or OpenStreetMap
# Dataset: Drainage network data
# Format: Shapefile or GeoJSON
# Access Method:
# Contact DWASA for official data.
# Use OpenStreetMap data to extract drainage-related features.
# Python Code to Download Drainage Data via Overpass API:
import overpy

api = overpy.Overpass()
# Define the bounding box
bbox = (23.6, 90.2, 23.95, 90.55)

# Query for drainage features
query = f"""
[out:json];
(
way["man_made"="storm_drain"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
way["waterway"="drain"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
);
out body;
>;
out skel qt;
"""

result = api.query(query)

# Process the data
# ... [Code to convert result to GeoDataFrame] ...


#   5. Population Data
# Source: Bangladesh Bureau of Statistics (BBS)
# Dataset: Population density data
# Format: Shapefile or CSV
# Access Method:
# Visit the BBS website to download census data.
# Alternatively, use global population datasets like WorldPop or GPWv4.
# Python Code to Download WorldPop Data:

import rasterio

# WorldPop download URL for Bangladesh
url = 'https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/BGD/bgd_ppp_2020.tif'

# Download the data
import requests

response = requests.get(url)
with open('data/bgd_population_2020.tif', 'wb') as f:
    f.write(response.content)