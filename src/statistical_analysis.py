"""
statistical_analysis.py
This script analyzes the correlation between rainfall and flood incidents.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def analyze_correlation(rainfall, flood_incidents):
    """
    Analyze correlation between rainfall and flood incidents.

    Parameters:
        rainfall (DataFrame): Rainfall data.
        flood_incidents (DataFrame): Flood incidents data.

    Returns:
        float: Correlation coefficient.
    """
    # Merge datasets on date
    rainfall_flood = pd.merge(rainfall, flood_incidents, on='date')

    # Calculate correlation
    correlation = rainfall_flood['rainfall_mm'].corr(rainfall_flood['flood_incident_count'])

    # Plotting
    sns.scatterplot(data=rainfall_flood, x='rainfall_mm', y='flood_incident_count')
    plt.title('Rainfall vs Flood Incidents in Dhaka')
    plt.xlabel('Daily Rainfall (mm)')
    plt.ylabel('Number of Flood Incidents')
    plt.show()

    return correlation