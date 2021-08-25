"""

Use this file to process and configure Sentinel-2 data.

"""
import affine
import xarray as xr
import shapely.geometry as sg
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import rasterio
import rasterio.features
import geopandas as gp
import geoplot as gplt
import os
import pandas as pd
import pickle
from tqdm import tqdm
from vis import plot_land_cover_map
pd.options.display.width = 0
pd.set_option('display.max_colwidth', None)


# Raster data to GeoDataframe: see https://stackoverflow.com/questions/67487713/python-how-to-convert-geotiff-to-geopanda

def polygonize(da: xr.DataArray) -> gp.GeoDataFrame:
    """
    Polygonize a 2D-DataArray into a GeoDataFrame of polygons. Polygon coordinates are ordened as (BR, BL, UL, UR).
    : param da: xr.DataArray with raster data

    Returns: polygonized : geopandas.GeoDataFrame with raster data
    """

    if da.dims != ("y", "x"):
        raise ValueError('Dimensions must be ("y", "x")')

    values = da.values
    transform = da.attrs.get("transform", None)
    if transform is None:
        raise ValueError("transform is required in da.attrs")
    transform = affine.Affine(*transform)
    shapes = rasterio.features.shapes(values, transform=transform)
    # shapes = A pair of (polygon, value) for each feature found in the image.

    geometries = []
    colvalues = []
    for idx, (geom, colval) in enumerate(shapes):
        if idx < 10:
            print(colval)
        # Swap x,y coordinates to get lat, lon
        poly_coords = [(y, x) for x, y in geom['coordinates'][0]]
        geometries.append(sg.Polygon(poly_coords))
        colvalues.append(colval)

    gdf = gp.GeoDataFrame({"value": colvalues, "geometry": geometries})

    # print(gdf.geometry)
    gdf.crs = da.attrs.get("crs")
    return gdf


def get_ndvi_loc(cloudmask):
    """Get NDVI raster location.
    :param cloudmask: Boolean variable if cloudmask is applied in data or not

    Returns: NDVI raster data.
    """

    # Data locations
    ndvi_path = r'./data/output/'

    # File names consist of CloudMask T(rue)/F(alse) + AGGregation factor.
    if cloudmask:
        # ndvi_raster = ndvi_path + 'ndvi_2017_cmtrue_0.0023898.tif'
        # ndvi_raster = ndvi_path + 'ndvi_2017_CMtRES1.tif'
        # ndvi_raster = ndvi_path + 'ndvi_2017_CMtRES0.023898.tif'
        # ndvi_raster = ndvi_path + 'ndvi_2017_CMtRES0.23898.tif'
        ndvi_raster = ndvi_path + 'ndvi_2017_CMtAGG33.tif'
    else:
        # ndvi_raster = ndvi_path + 'ndvi_2017_cmfalse_0.0023898.tif'
        # ndvi_raster = ndvi_path + 'ndvi_2017_cmfalse_noreproject.tif'
        # ndvi_raster = ndvi_path + 'ndvi_2017_cmfalse_0.023898.tif'
        ndvi_raster = ndvi_path + 'ndvi_2017_cmfalse_1.tif'

    return ndvi_raster


def get_ndvi_gdf(preload, cloudmask, survey_area):
    """Polygonize raster.

    Parameters:
    :param preload: Boolean variable to decide whether to preload existing data or to fetch new.
    :param cloudmask: Boolean variable if clouds should be masked in data( = set to -1).
    :param survey_area: Shapely Polygon of survey area.

    Returns: GeoDataframe with values & geometry.
    """

    if preload:
        print("Loading existing NDVI data...")
        gdf_ndvi = pickle.load(open("./data/pickled/gdf_ndvi.p", "rb"))
        print("NDVI data loaded!")
    else:
        print("Fetching new NDVI data...")
        # Get location
        raster = get_ndvi_loc(cloudmask)
        # Open as raster
        x_arr = xr.open_rasterio(raster).squeeze('band', drop=True)
        # Save attributes to put back later
        attributes = x_arr.attrs

        #  - y / lat: 39 -> 36, x / lon: -1 -> 3 [UL, UR, BL, BR] = [(3, 36),(3, 39),(-1, 36),(-1, 39)]
        # print(x_arr)
        # # Seems like 'NoData' values are filled with -3.4e38. Clip those to -1 (barren environment = not suitable)
        # # print(np.amin(ndvi)); ndvi = np.where(ndvi < -10000000, -1, ndvi)

        # This function removes attributes
        x_arr = xr.where(x_arr < -10000000, -1, x_arr)
        # Re-add attributes
        x_arr = x_arr.assign_attrs(attributes)
        # Get GeoDataframe from DataArray
        gdf_ndvi = polygonize(x_arr)

        # Only keep NDVI patches within survey area
        gdf_ndvi = gdf_ndvi.loc[lambda _df: _df['geometry'].within(
            survey_area)]

        # Set unique indices
        ndvi_index = pd.Index(['NDVI' + str(idx)
                               for idx in range(len(gdf_ndvi))])
        gdf_ndvi.set_index(ndvi_index, inplace=True)

        # Save data locally.
        pickle.dump(gdf_ndvi, open("./data/pickled/gdf_ndvi.p", "wb"))
        print("NDVI data loaded and saved locally.")

    return gdf_ndvi
