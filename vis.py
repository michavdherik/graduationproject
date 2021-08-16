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

    # fig, ax = plt.subplots(1, 1) scale=name, limits=(2, 16), legend=True, legend_var='scale', legend_kwargs={'loc': 'lower right'}
    ax = gplt.pointplot(gdf, ax=ax, scale=name, limits=(2, 16), color=COLOR, edgecolor='black', zorder=2,
                        legend=True, legend_var='scale', legend_kwargs={'loc': 'lower right'})
    ax = gplt.kdeplot(gdf, shade=True, cmap=CMAP, alpha=0.5, zorder=1, ax=ax)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    ax.set_title(f'{name} Population in Samburu', fontsize=16)
    plt.show()
    return


def plot_aerial_tracks(gdf, ax):
    """
    Plot aerial tracks.
    :param gdf: GeoDataframe holding flight track data.
    """

    #fig, ax = plt.subplots(1, 1)
    ax = gplt.sankey(gdf['geometry'], color='green',
                     zorder=1, alpha=0.8, ax=ax)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    #ax.set_title('Flight Tracks in Samburu', fontsize=16)
    plt.show()
    return


def plot_blocks(gdf, ax):
    """
    Plot flight track blocks.
    :param gdf: GeoDataframe holding block data.
    :param ax: Figure to plot block data onto.
    """

    #fig, ax = plt.subplots(1, 1)
    ax = gplt.polyplot(gdf, color='blue', zorder=2, alpha=0.8, ax=ax)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    #ax.set_title('Flight Tracks in Samburu', fontsize=16)
    plt.show()
    return


def plot_land_cover_map(gdf, ax):
    """
    Plot NDVI map.
    :param gdf: GeoDataframe holding block data.
    :param ax: Figure to plot block data onto.
    """

    gdf.plot(column='value', cmap='Greens', ax=ax, legend=True)
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)
    plt.show()
    return
