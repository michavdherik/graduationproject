"""

Use this file to preprocess data.

"""
from typing import Tuple
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, Polygon
import numpy as np
import geopandas as gp
import os
import pandas as pd
pd.options.display.width = 0

# Data locations
census_path = r'./data/census/'
flight_path = r'./data/tracks/'
poly_path = r'./data/geometries/'
block_path = r'./data/blocks/'

# Read data
gdf_2008 = gp.read_file(os.path.join(
    census_path, 'census_data_2008.shp'))
gdf_2017 = gp.read_file(os.path.join(
    census_path, 'census_data_2017.shp'))


def get_2008_population_data() -> Tuple[Tuple[gp.GeoDataFrame, str], Tuple[gp.GeoDataFrame, str]]:
    """Processes and returns 2008 population data.
    Tuple including data from elephants and buffalos. Each animal is a Tuple of (gdf, name).

    Returns: Tuple of Tuples with population data."""

    gdf = gdf_2008

    # Get elephants & buffalos only, remove rows with no animal observations
    gdf_el = gdf.drop(gdf.iloc[:, np.r_[12:27, 28:63]], axis=1)
    gdf_el = gdf_el[gdf_el['EL'] > 0]
    gdf_el.reset_index(drop=True, inplace=True)
    el_counts = gdf_el['EL'].tolist()

    gdf_bf = gdf.drop(gdf.iloc[:, np.r_[12:14, 15:63]], axis=1)
    gdf_bf = gdf_bf[gdf_bf['BF'] > 0]
    bf_counts = gdf_bf['BF'].tolist()

    return (gdf_el, 'EL'), (gdf_bf, 'BF')


def get_track_data() -> gp.GeoDataFrame:
    """Processes and returns flight track data."""

    # Get aerial tracks
    tracksdf = gp.read_file(os.path.join(
        flight_path, 'Flightlines_2017.shp'))
    # Properties:
    # ~ 1km horizontal difference between tracks

    # Remove NaNs
    tracksdf.dropna(how='any', subset=['geometry'], inplace=True)

    return tracksdf


def get_block_data() -> gp.GeoDataFrame:
    """Processes and returns block data."""

    # Get block data
    blocksdf = gp.read_file(os.path.join(
        block_path, 'blocks_2017.shp'))

    # Remove NaNs
    blocksdf.dropna(how='any', inplace=True)

    return blocksdf


def get_2017_population_data() -> Tuple[Tuple[gp.GeoDataFrame, str], Tuple[gp.GeoDataFrame, str]]:
    """Processes and returns 2008 population data: Tuple of (gdf, name)

    Returns: Tuple of Tuples with population data."""

    gdf = gdf_2017

    # Get elephants & buffalos only, remove rows with no elephants or buffalos
    gdf_el = gdf.loc[gdf['Species'] == 'EL']
    gdf_el['EL'] = gdf_el['Estimate']
    gdf_el = gdf_el[gdf_el['EL'] > 0]
    # Remove outlier point in the middle of the sea
    gdf_el = gdf_el[gdf_el['X'] > 0]

    gdf_bf = gdf.loc[gdf['Species'] == 'BF']
    gdf_bf['BF'] = gdf_bf['Estimate']
    gdf_bf = gdf_bf[gdf_bf['BF'] > 0]

    # Make new indicies
    el_index = pd.Index(['Obs' + str(idx) for idx in range(len(gdf_el))])
    bf_index = pd.Index(['Obs' + str(idx) for idx in range(len(gdf_bf))])

    # Set new indices
    gdf_el.set_index(el_index, inplace=True)
    gdf_bf.set_index(bf_index, inplace=True)

    print("Animal data loaded!")

    return (gdf_el, 'EL'), (gdf_bf, 'BF')


def get_aoi() -> None:
    """
    If not present, create simple circumference polygon to project NDVI data, and write to output location. 
    This function is run once.
    """

    # Get block data
    blocksdf = get_block_data()

    # Get union
    union = blocksdf['geometry'].unary_union
    # Remove Polygon holes. (This also removes wanted holes, such as a lake. The lake can be avoided using NDVI/Elevation data.)
    union = Polygon(list(union.exterior.coords))

    # Convert to dataframe
    union_df = gp.GeoDataFrame(geometry=[union], crs=blocksdf.crs)

    schema = {'geometry': 'Polygon'}

    # Write a new Shapefile
    with fiona.open(os.path.join(poly_path, 'Census2017Polygon-filled.shp'), 'w',
                    crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as c:
        c.write({
            'geometry': mapping(union),
        })
