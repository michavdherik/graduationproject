"""

Use this file for any visualisations.

"""

# from affine import Affine
# from rasterio.plot import show
# import rasterio
import os
import contextily as ctx
import geoplot as gplt
from osgeo import gdal
import matplotlib.pyplot as plt


def plot_density(gdf, name, ax):
    """Plot the density and locations of a specific species.
    :param gdf: GeoDataframe holding population count values for a species.
    :param name: Name of species to visualize. Currently only elephant ('EL')  / buffalo ('BF') available. 

    """
    if name == 'EL':
        COLOR, CMAP = ['Red', 'Reds']
    elif name == 'BF':
        COLOR, CMAP = ['Blue', 'Blues']

    #fig, ax = plt.subplots(1, 1)
    ax = gplt.pointplot(gdf, ax=ax, scale=name, color=COLOR, limits=(
        2, 16), edgecolor='black', zorder=2, legend=True, legend_var='scale', legend_kwargs={'loc': 'lower right'})
    ax = gplt.kdeplot(gdf, shade=True, cmap=CMAP, alpha=0.5, zorder=1, ax=ax)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    ax.set_title(f'{name} Population in Samburu', fontsize=16)
    # plt.show()
    return


def plot_aerial_tracks(gdf, ax):
    """
    Plot aerial tracks.
    :param gdf: GeoDataframe holding flight track data.
    """

    #fig, ax = plt.subplots(1, 1)
    ax = gplt.sankey(gdf, color='green', zorder=1, alpha=0.8, ax=ax)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    ax.set_title('Flight Tracks in Samburu', fontsize=16)
    plt.show()
    return


def plot_land_cover_map(gdf):
    """
    Plot land cover map.
    """
    return

###  Plot land cover map ###
# Read land cover map
# landcover_path = r'./data/Kenya_Sentinel2_LULC2016/Kenya_Sentinel2_LULC2016.tif'

# Get window
# ulx, uly, lrx, lry = [3, 36, -0.2, 39]
# xmax, ymax, xmin, ymin = [3, 36, -0.2, 39]
# def window_from_extent(xmin, xmax, ymin, ymax, aff):
#     col_start, row_start = ~aff * (xmin, ymax)
#     col_stop, row_stop = ~aff * (xmax, ymin)
#     return ((int(row_start), int(row_stop)), (int(col_start), int(col_stop)))


# Transform
# with rasterio.open(landcover_path) as src:
#     aff = src.transform
#     meta = src.meta.copy()
#     window = window_from_extent(xmin, xmax, ymin, ymax, aff)
#     # Read cropped array
#     arr = src.read(1, window=window)
#     # Update dataset metadata (if you need it)
#     meta.update(height=window[0][1] - window[0][0],
#                 width=window[1][1] - window[1][0],
#                 affine=src.window_transform(window))
#     meta.pop('transform', None)

# show(arr)
