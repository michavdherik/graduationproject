"""

Use this file to preprocess data.

"""
# %%
from vis import plot_density, plot_aerial_tracks
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gp
import os
import pandas as pd
pd.options.display.width = 0

# Data locations
census_path = r'./data/census/'
flight_path = r'./data/tracks/'

# dbf, shx file automatically read
gdf = gp.read_file(os.path.join(census_path, 'smb_aerialsurvey_nov2008.shp'))

# plot elephants / buffalos only, remove rows with no elephants or buffalos
gdf_el = gdf.drop(gdf.iloc[:, np.r_[12:27, 28:63]], axis=1)
gdf_el = gdf_el[gdf_el['EL'] > 0]
el_counts = gdf_el['EL'].tolist()

gdf_bf = gdf.drop(gdf.iloc[:, np.r_[12:14, 15:63]], axis=1)
gdf_bf = gdf_bf[gdf_bf['BF'] > 0]
bf_counts = gdf_bf['BF'].tolist()

# Visualize species density
# fig, ax = plt.subplots(1, 1)
#plot_density(gdf=gdf_el, name='EL')
#plot_density(gdf=gdf_bf, name='BF')

# Get aerial tracks
tracksdf = gp.read_file(os.path.join(
    flight_path, 'smb_laik_msbt_tracks_2008.shp'))

# Remove NaNs
tracksdf.dropna(how='any', subset=['geometry'], inplace=True)
print(tracksdf)

# Visualize flight paths
# plot_aerial_tracks(gdf=tracksdf)


# %%
