"""
visualization.py
This script generates visualizations for the flood risk analysis.
"""

import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx

def plot_flood_risk_map(flood_risk_data):
    """
    Plot the flood risk map.

    Parameters:
        flood_risk_data (GeoDataFrame): Spatial data with risk levels.
    """
    fig, ax = plt.subplots(figsize=(12, 12))
    flood_risk_data.plot(column='risk_level', cmap='Reds', legend=True, ax=ax)

    # Add basemap
    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

    plt.title('Flood Risk Map of Dhaka')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

def plot_rainfall_vs_flood_incidents(rainfall_flood_data):
    """
    Plot rainfall vs flood incidents.

    Parameters:
        rainfall_flood_data (DataFrame): Merged rainfall and flood incidents data.
    """
    sns.scatterplot(data=rainfall_flood_data, x='rainfall_mm', y='flood_incident_count')
    plt.title('Rainfall vs Flood Incidents in Dhaka')
    plt.xlabel('Daily Rainfall (mm)')
    plt.ylabel('Number of Flood Incidents')
    plt.show()