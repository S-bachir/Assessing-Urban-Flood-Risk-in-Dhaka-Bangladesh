"""
data_loading.py
This script contains functions to load and preprocess all necessary datasets(data from API).
"""


import requests
import geopandas as gpd
import pandas as pd
import os
# import requests_cache
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# import openmeteo_requests
# OPENMETEO_AVAILABLE = True
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry




import numpy as np
from osgeo import gdal
from shapely.geometry import box




def get_coordinates(location):
    geolocator = Nominatim(user_agent="my_agent")
    try:
        # Attempt to geocode the location
        location_data = geolocator.geocode(location, timeout=10)
        
        if location_data:
            latitude = location_data.latitude
            longitude = location_data.longitude
            return latitude, longitude
        else:
            return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        print("Error: Geocoding service timed out or unavailable. Please try again later.")
        return None, None

# Example usage
location = "Niamey, Niger"
lat, lon = get_coordinates(location)

if lat and lon:
    print(f"Coordinates for {location}:")
    print(f"Latitude: {lat}")
    print(f"Longitude: {lon}")
else:
    print(f"Could not find coordinates for {location}")




def temp_humi_rain_data(latitude, longitude):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2000-01-01",
        "end_date": "2024-01-01",
        "daily": ["temperature_2m_mean", "apparent_temperature_mean", "precipitation_sum", "rain_sum"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
    daily_apparent_temperature_mean = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(3).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
    daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["latitude"] = latitude
    daily_data["longitude"] = longitude
    daily_dataframe = pd.DataFrame(data = daily_data)

    return daily_dataframe



def flood_data(latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": 59.91,
        "longitude": 10.75,
        "daily": ["river_discharge", "river_discharge_mean", "river_discharge_median", "river_discharge_max", "river_discharge_min"],
        "start_date": "2000-01-01",
        "end_date": "2024-01-01"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_river_discharge = daily.Variables(0).ValuesAsNumpy()
    daily_river_discharge_mean = daily.Variables(1).ValuesAsNumpy()
    daily_river_discharge_median = daily.Variables(2).ValuesAsNumpy()
    daily_river_discharge_max = daily.Variables(3).ValuesAsNumpy()
    daily_river_discharge_min = daily.Variables(4).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["river_discharge"] = daily_river_discharge
    daily_data["river_discharge_mean"] = daily_river_discharge_mean
    daily_data["river_discharge_median"] = daily_river_discharge_median
    daily_data["river_discharge_max"] = daily_river_discharge_max
    daily_data["river_discharge_min"] = daily_river_discharge_min

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe



def climate_data(latitude, longitude):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://climate-api.open-meteo.com/v1/climate"
    params = {
        "latitude": 13.5137,
        "longitude": 2.1098,
        "start_date": "2000-01-01",
        "end_date": "2024-01-01",
        "daily": ["shortwave_radiation_sum", "pressure_msl_mean", "soil_moisture_0_to_10cm_mean", "et0_fao_evapotranspiration_sum"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_shortwave_radiation_sum = daily.Variables(0).ValuesAsNumpy()
    daily_pressure_msl_mean = daily.Variables(1).ValuesAsNumpy()
    daily_soil_moisture_0_to_10cm_mean = daily.Variables(2).ValuesAsNumpy()
    daily_et0_fao_evapotranspiration_sum = daily.Variables(3).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
    daily_data["pressure_msl_mean"] = daily_pressure_msl_mean
    daily_data["soil_moisture_0_to_10cm_mean"] = daily_soil_moisture_0_to_10cm_mean
    daily_data["et0_fao_evapotranspiration_sum"] = daily_et0_fao_evapotranspiration_sum

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe


def load_rainfall_data(filepath):
    """
    Load and preprocess rainfall data.

    Parameters:
        filepath (str): Path to the rainfall CSV file.

    Returns:
        pandas.DataFrame: Processed rainfall data.
    """
    rainfall = pd.read_csv(filepath, parse_dates=['date'])
    return rainfall

def load_dem_data(filepath):
    """
    Load and preprocess DEM data.

    Parameters:
        filepath (str): Path to the DEM TIFF file.

    Returns:
        geopandas.GeoDataFrame: DEM data as a GeoDataFrame.
    """
    dem_dataset = gdal.Open(filepath)
    dem_array = dem_dataset.ReadAsArray()
    gt = dem_dataset.GetGeoTransform()
    proj = dem_dataset.GetProjection()

    # Create coordinates
    nrows, ncols = dem_array.shape
    x0, dx, _, y0, _, dy = gt
    x = np.linspace(x0, x0 + dx * ncols, ncols)
    y = np.linspace(y0, y0 + dy * nrows, nrows)
    xv, yv = np.meshgrid(x, y)

    # Flatten the arrays
    elevation = dem_array.flatten()
    xs = xv.flatten()
    ys = yv.flatten()

    # Create GeoDataFrame
    dem_gdf = gpd.GeoDataFrame({'elevation': elevation}, geometry=gpd.points_from_xy(xs, ys))
    dem_gdf.crs = proj
    return dem_gdf

def load_land_use_data(filepath):
    """
    Load land use data.

    Parameters:
        filepath (str): Path to the land use shapefile.

    Returns:
        geopandas.GeoDataFrame: Land use data.
    """
    land_use = gpd.read_file(filepath)
    return land_use

def load_drainage_data(filepath):
    """
    Load drainage infrastructure data.

    Parameters:
        filepath (str): Path to the drainage shapefile.

    Returns:
        geopandas.GeoDataFrame: Drainage data.
    """
    drainage = gpd.read_file(filepath)
    return drainage

def load_population_data(filepath):
    """
    Load population density data.

    Parameters:
        filepath (str): Path to the population shapefile.

    Returns:
        geopandas.GeoDataFrame: Population data.
    """
    population = gpd.read_file(filepath)
    return population


# Global Health Observatory (WHO): Comprehensive Health-Related Statistics
# The WHO's Global Health Observatory provides an OData API for accessing health-related statistics.
def get_life_expectancy_data():
    import pandas as pd
    import requests

    # WHO GHO OData API endpoint for Life Expectancy at Birth (Indicator Code: WHOSIS_000001)
    url = "https://ghoapi.azureedge.net/api/WHOSIS_000001"

    # Retrieve data
    response = requests.get(url)
    data = response.json()

    # Convert data to DataFrame
    df = pd.json_normalize(data['value'])

    # Display the first few rows
    return df



# World Bank Open Data: Socioeconomic Indicators and Development Data
# The World Bank offers an API to access a wide range of socioeconomic data.
def get_world_bank_gdp_data(countries):
    import pandas as pd
    from pandas_datareader import wb

    # Specify the indicator code for GDP
    indicator = 'NY.GDP.MKTP.CD'

    # Retrieve data
    data = wb.download(indicator=indicator, country=countries, start=2000, end=2020)

    # Reset index for easy handling
    data.reset_index(inplace=True)

    # Display the data
    return data


# Demographic and Health Surveys (DHS): Detailed Household and Health Data
# DHS provides surveys with detailed health and demographic data.
def get_dhs_data(country_code):
    import pandas as pd
    import requests

    # DHS API endpoint
    url = "https://api.dhsprogram.com/rest/dhs/data"

    # Parameters for the API request
    params = {
        'countryIds': country_code,
        'surveyType': 'DHS',
        'format': 'json'
    }

    # Retrieve data
    response = requests.get(url, params=params)
    data = response.json()

    # Convert data to DataFrame
    df = pd.json_normalize(data['Data'])

    # Display the data
    return df.head()



# Climate Data Platforms: WorldClim for High-Resolution Climate Data
# WorldClim provides free climate data for ecological modeling and GIS.
def download_worldclim_data(var, res):
    import os
    import rasterio
    import urllib.request

    # Base URL for WorldClim data
    base_url = f'http://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_{res}m_{var}.zip'

    # Download destination
    dest = f'worldclim_{var}_{res}m.zip'

    # Download the data
    urllib.request.urlretrieve(base_url, dest)

    # Unzip the downloaded file
    from zipfile import ZipFile
    with ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(f'worldclim_{var}_{res}m')

    # List unzipped files
    files = os.listdir(f'worldclim_{var}_{res}m')
    return files



# Remote Sensing Databases: MODIS for Environmental and Land Cover Data
# MODIS provides satellite data for environmental monitoring.
def get_modis_ndvi(region):
    import ee

    # Initialize the Earth Engine module.
    ee.Initialize()

    # Define the region of interest
    roi = ee.Geometry.Polygon(region)

    # Get MODIS NDVI data
    modis_ndvi = ee.ImageCollection('MODIS/006/MOD13A2').select('NDVI')

    # Filter data for the region
    modis_ndvi_region = modis_ndvi.mean().clip(roi)

    # Get the URL for downloading the image
    url = modis_ndvi_region.getDownloadURL({
        'scale': 500,
        'region': roi.coordinates().getInfo()
    })

    # Return the download URL
    return url


region_coords = [[
    [2.05, 13.5],
    [2.15, 13.5],
    [2.15, 13.6],
    [2.05, 13.6],
    [2.05, 13.5]
]]

ndvi_download_url = get_modis_ndvi(region_coords)
print(ndvi_download_url)