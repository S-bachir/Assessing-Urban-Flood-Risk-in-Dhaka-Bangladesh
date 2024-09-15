"""
spatial_analysis.py
This script performs spatial analysis to identify high-risk flood areas.
"""

import geopandas as gpd
import numpy as np

def prepare_spatial_data(land_use, dem, drainage, population):
    """
    Combine spatial datasets into a single GeoDataFrame.

    Parameters:
        land_use (GeoDataFrame): Land use data.
        dem (GeoDataFrame): Digital Elevation Model data.
        drainage (GeoDataFrame): Drainage infrastructure data.
        population (GeoDataFrame): Population density data.

    Returns:
        GeoDataFrame: Combined spatial data.
    """
    # Ensure all datasets have the same CRS
    common_crs = 'EPSG:4326'
    land_use = land_use.to_crs(common_crs)
    dem = dem.to_crs(common_crs)
    drainage = drainage.to_crs(common_crs)
    population = population.to_crs(common_crs)

    # Spatially join datasets
    spatial_data = gpd.sjoin(land_use, dem, how='inner', op='intersects')
    spatial_data = gpd.sjoin(spatial_data, drainage, how='left', op='intersects')
    spatial_data = gpd.sjoin(spatial_data, population, how='left', op='intersects')

    return spatial_data

def identify_high_risk_areas(spatial_data, thresholds):
    """
    Identify high-risk flood areas based on criteria.

    Parameters:
        spatial_data (GeoDataFrame): Combined spatial data.
        thresholds (dict): Dictionary of threshold values.

    Returns:
        GeoDataFrame: Spatial data with risk levels assigned.
    """
    # Define criteria for high risk
    high_risk_conditions = (
        (spatial_data['elevation'] < thresholds['elevation']) &
        (spatial_data['drainage_capacity'].fillna(0) < thresholds['drainage_capacity']) &
        (spatial_data['population_density'] > thresholds['population_density'])
    )

    spatial_data['risk_level'] = np.where(high_risk_conditions, 'High', 'Low')
    return spatial_data