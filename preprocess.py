"""

Use this file to preprocess data.

"""

from vis import plot_density, plot_aerial_tracks
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gp
import os
import pandas as pd
#from model import GeoAgent, AnimalModel
pd.options.display.width = 0

# Data locations
census_path = r'./data/census/'
flight_path = r'./data/tracks/'

# dbf, shx file automatically read
gdf = gp.read_file(os.path.join(census_path, 'smb_aerialsurvey_nov2008.shp'))
# gdf.reset_index(level=0, inplace=True)  # set index as unique id column


def get_population_data():
    """Returns population data: Tuple of (gdf, name)"""

    # plot elephants / buffalos only, remove rows with no elephants or buffalos
    gdf_el = gdf.drop(gdf.iloc[:, np.r_[12:27, 28:63]], axis=1)
    gdf_el = gdf_el[gdf_el['EL'] > 0]
    gdf_el.reset_index(drop=True, inplace=True)
    el_counts = gdf_el['EL'].tolist()

    gdf_bf = gdf.drop(gdf.iloc[:, np.r_[12:14, 15:63]], axis=1)
    gdf_bf = gdf_bf[gdf_bf['BF'] > 0]
    bf_counts = gdf_bf['BF'].tolist()

    # gdf_el = gdf_el.head(3)
    # gdf_bf = gdf_bf.head(10)

    return (gdf_el, 'EL'), (gdf_bf, 'BF')


# def population_for_model(gdf, name):
#     gdf_new = gdf.filter(['geometry', name], axis=1)
#     return gdf_new


def get_track_data():
    """Returns flight track data."""

    # Visualize species density
    #fig, ax = plt.subplots(1, 1)
    #plot_density(gdf=gdf_el, name='EL', ax=ax)
    #plot_density(gdf=gdf_bf, name='BF', ax=ax)

    # Get aerial tracks
    tracksdf = gp.read_file(os.path.join(
        flight_path, 'smb_laik_msbt_tracks_2008.shp'))
    # Properties:
    # ~ 1km horizontal difference between tracks

    # Remove NaNs
    tracksdf.dropna(how='any', subset=['geometry'], inplace=True)

    # Visualize flight paths
    #plot_aerial_tracks(gdf=tracksdf, ax=ax)

    return tracksdf


# Calculate cover of aerial flight paths.
# Variables, in meter
TRANSECT_WIDTH = 2500
OBSERVER_STRIP = 141
BLIND_SPOT = 250

# TODO: Determine how many animals would be spotted if only 10% of flight paths would be flown etc.
# # Assume current flight data = 100% animals visible.
# # Determine % of population seen if number of flights is decreased.
