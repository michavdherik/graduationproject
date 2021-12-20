"""

Use this file to process and configure Sentinel-2 data.

"""
import affine
import xarray as xr
import shapely.geometry as sg
import rasterio
import rasterio.features
import geopandas as gp
import pandas as pd
import pickle
pd.options.display.width = 0
pd.set_option('display.max_colwidth', None)


def polygonize(da: xr.DataArray) -> gp.GeoDataFrame:
    """
    Polygonize a 2D-DataArray into a GeoDataFrame of polygons. Polygon coordinates are ordened as (BR, BL, UL, UR).
    :param da: xr.DataArray with raster data

    Returns: polygonized: gp.GeoDataFrame with raster data
    """

    if da.dims != ("y", "x"):
        raise ValueError('Dimensions must be ("y", "x")')

    values = da.values
    transform = da.attrs.get("transform", None)
    if transform is None:
        raise ValueError("transform is required in da.attrs")
    transform = affine.Affine(*transform)
    shapes = rasterio.features.shapes(values, transform=transform)

    geometries = []
    colvalues = []
    for idx, (geom, colval) in enumerate(shapes):
        # Swap x,y coordinates to get lat, lon
        poly_coords = [(y, x) for x, y in geom['coordinates'][0]]
        geometries.append(sg.Polygon(poly_coords))
        colvalues.append(colval)

    gdf = gp.GeoDataFrame({"value": colvalues, "geometry": geometries})

    gdf.crs = da.attrs.get("crs")
    return gdf


def get_ndvi_loc(cloudmask) -> str:
    """Get NDVI raster location.
    :param cloudmask: Boolean variable if cloudmask is applied in data or not

    Returns: gdf: string with data location of raster data.
    """

    # Data locations
    ndvi_path = r'./data/output/'

    # File names consist of CloudMask T(rue)/F(alse) + AGGregation factor.
    if cloudmask:
        ndvi_raster = ndvi_path + 'ndvi_2017_CMtAGG33.tif'
    else:
        ndvi_raster = ndvi_path + 'ndvi_2017_CMfAGG33.tif'

    return ndvi_raster


def get_ndvi_gdf(preload, cloudmask, survey_area) -> gp.GeoDataFrame:
    """Polygonize raster.

    Parameters:
    :param preload: Boolean variable to decide whether to preload existing data or to fetch new.
    :param cloudmask: Boolean variable if clouds should be masked in data( = set to -1).
    :param survey_area: Shapely Polygon of survey area.

    Returns: gdf_ndvi: gp.GeoDataframe with NDVI values & geometry.
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
