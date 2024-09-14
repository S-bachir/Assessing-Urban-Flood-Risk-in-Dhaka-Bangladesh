import requests
import geopandas as gpd
import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

import matplotlib as plt
import geoviews.feature as gf
import xarray as xr
from cartopy import crs
from geoviews import opts
import geoviews as gv
gv.extension('bokeh', 'matplotlib')
import geopandas as gpd
import seaborn as sns

# for basemaps
import contextily as ctx

# For spatial statistics
import esda
from esda.moran import Moran, Moran_Local

import splot
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster,plot_moran_simulation

import libpysal as lps

# Graphics
import matplotlib.pyplot as plt
import plotly.express as px







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