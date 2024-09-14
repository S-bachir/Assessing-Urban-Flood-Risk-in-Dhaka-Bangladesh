






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