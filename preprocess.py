"""

Use this file to preprocess data.

"""

import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, Polygon
from vis import plot_density, plot_aerial_tracks, plot_blocks
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gp
import os
import math
import pandas as pd
import contextily as ctx
pd.options.display.width = 0

# Data locations
census_path = r'./data/census/'
flight_path = r'./data/tracks/'
poly_path = r'./data/geometries/'
block_path = r'./data/blocks/'

# Read data
gdf_2008 = gp.read_file(os.path.join(
    census_path, 'smb_aerialsurvey_nov2008.shp'))
gdf_2017 = gp.read_file(os.path.join(
    census_path, 'LKPSMB_MSBT_MRU_2017FINAL.shp'))
block_2017 = gp.read_file(os.path.join(block_path, ''))


def get_population_data():
    """Returns population data: Tuple of (gdf, name)"""

    gdf = gdf_2008

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


def get_track_data():
    """Returns flight track data."""

    # Visualize species density
    # fig, ax = plt.subplots(1, 1)
    # plot_density(gdf=gdf_el, name='EL', ax=ax)
    # plot_density(gdf=gdf_bf, name='BF', ax=ax)

    # Get aerial tracks
    tracksdf = gp.read_file(os.path.join(
        flight_path, 'Flightlines 2017 merged.shp'))
    # Properties:
    # ~ 1km horizontal difference between tracks

    # Remove NaNs
    tracksdf.dropna(how='any', subset=['geometry'], inplace=True)

    # # Visualize flight paths
    # fig, ax = plt.subplots()
    # plot_aerial_tracks(gdf=tracksdf, ax=ax)
    # plt.show()

    return tracksdf


def get_block_data():
    """Returns block data."""

    # Get block data
    blocksdf = gp.read_file(os.path.join(
        block_path, 'revised2017blocks_edited_projected.shp'))

    # Select relevant columns, set to normal projection
    blocksdf = gp.GeoDataFrame(geometry=blocksdf['geometry'].to_crs(4326))

    # Remove NaNs
    blocksdf.dropna(how='any', inplace=True)

    # Visualize flight blocks
    # fig, ax = plt.subplots()
    # plot_blocks(gdf=blocksdf, ax=ax)

    return blocksdf


def get_2017_population_data():
    """Get and preprocess 2017 data."""

    # gdf.to_csv('out.csv')
    # print(gdf.info(verbose=True))
    # print(gdf.head())
    gdf = gdf_2017

    gdf_el = gdf.loc[gdf['Species'] == 'EL']
    gdf_el['EL'] = gdf_el['Estimate']
    gdf_el = gdf_el[gdf_el['EL'] > 0]
    # remove outlier point in the middle of the sea
    gdf_el = gdf_el[gdf_el['X'] > 0]
    # gdf_el.reset_index(drop=True, inplace=True)

    gdf_bf = gdf.loc[gdf['Species'] == 'BF']
    gdf_bf['BF'] = gdf_bf['Estimate']
    gdf_bf = gdf_bf[gdf_bf['BF'] > 0]
    # gdf_bf.reset_index(drop=True, inplace=True)

    el_index = pd.Index(['Obs' + str(idx) for idx in range(len(gdf_el))])
    bf_index = pd.Index(['Obs' + str(idx) for idx in range(len(gdf_bf))])

    gdf_el.set_index(el_index, inplace=True)
    gdf_bf.set_index(bf_index, inplace=True)

    print("Animal data loaded!")

    return (gdf_el, 'EL'), (gdf_bf, 'BF')


def get_aoi():
    """
    W.I.P. Create more accurate aoi Polygon from block data.

    Create simple circumference polygon to project NDVI data, and write to output location. (Do this once)
    :param gdf: GeoDataFrame holding census data.
    """

    # Get block data
    blocksdf = get_block_data()

    # Get union
    union = blocksdf['geometry'].unary_union
    # Remove Polygon holes. (This also removes wanted holes, such as a lake. The lake can be avoided using NDVI/Elevation data.)
    union = Polygon(list(union.exterior.coords))

    # Convert to dataframe
    union_df = gp.GeoDataFrame(geometry=[union], crs=blocksdf.crs)

    # Visualize flight blocks
    # fig, ax = plt.subplots()
    # plot_blocks(gdf=union_df, ax=ax)

    schema = {'geometry': 'Polygon'}

    # Write a new Shapefile
    with fiona.open(os.path.join(poly_path, 'Census2017Polygon-filled.shp'), 'w',
                    crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as c:
        c.write({
            'geometry': mapping(union),
        })


# minx, maxx, miny, maxy = (min(gdf['X']),
#                           max(gdf['X']),
#                           min(gdf['Y']),
#                           max(gdf['Y']))
# # extend bboxes
# minx, miny = (math.floor(minx), math.floor(miny))
# maxx, maxy = (math.ceil(maxx), math.ceil(maxy))
# # Min x:36.3135,, Max x:38.54945, Min y:-0.31092,x Max y:2.59046
# bbox = [(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx)]
# poly = Polygon(bbox)


# write_aoi()

# Step 1: Get Polygons
# Get union of all Polygons
# Export as Polygon

# Step 2: Export new NDVI map in R using new Polygon
# Step 3: bound movement of animal within Polygon
#
# In move_animal: calculate new coords and check whether there's a NDVI patch under it. if no, then must be outside bounds.

# List(List(Tuple(exterior coordinates) of each block), ...), ...)
# Calculate cover of aerial flight paths.
# Variables, in meter
TRANSECT_WIDTH = 2500
OBSERVER_STRIP = 141
BLIND_SPOT = 250

# TODO: Determine how many animals would be spotted if only 10% of flight paths would be flown etc.
# # Assume current flight data = 100% animals visible.
# # Determine % of population seen if number of flights is decreased.
