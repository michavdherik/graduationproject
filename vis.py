"""

Use this file for any visualisations.

"""

import contextily as ctx
import geoplot as gplt
from osgeo import gdal
import matplotlib.pyplot as plt


def plot_density(gdf, name) -> None:
    """Plot the density and locations of a specific species.
    :param gdf: GeoDataframe holding population count values for a species.
    :param name: Name of species to visualize. Currently only elephant ('EL')  / buffalo ('BF') available. 
    """

    # Set colors
    if name == 'EL':
        COLOR, CMAP = ['Red', 'Reds']
    elif name == 'BF':
        COLOR, CMAP = ['Blue', 'Blues']

    # Construct figure for visualization
    fig, ax = plt.subplots(1, 1)
    # Pointplot showing animals, scaled with number of observations
    ax = gplt.pointplot(gdf, ax=ax, scale=name, limits=(2, 16), color=COLOR, edgecolor='black', zorder=2,
                        legend=True, legend_var='scale', legend_kwargs={'loc': 'lower right'})
    # KDEplot showing distribution of animals.
    ax = gplt.kdeplot(gdf, shade=True, cmap=CMAP, alpha=0.5, zorder=1, ax=ax)

    # Add geographical reference map
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)

    # Set title
    ax.set_title(f'{name} Population', fontsize=16)

    # Show figure
    plt.show()


def plot_aerial_tracks(gdf) -> None:
    """
    Plot aerial tracks.
    :param gdf: GeoDataframe holding flight track data.
    """

    # Construct figure for visualization
    fig, ax = plt.subplots(1, 1)

    # Sanky plot showing flight lines
    gplt.sankey(gdf['geometry'], color='green',
                zorder=1, alpha=0.8, ax=ax)

    # Add geographical reference map
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)

    # Set title
    ax.set_title('Flight Tracks', fontsize=16)

    # Show figure
    plt.show()


def plot_blocks(gdf) -> None:
    """
    Plot flight track blocks.
    :param gdf: GeoDataframe holding block data.
    """

    # Construct figure for visualization
    fig, ax = plt.subplots(1, 1)

    # Polygonplot showing flight block data
    ax = gplt.polyplot(gdf, edgecolor='blue', zorder=2, alpha=0.8, ax=ax)

    # Add geographical reference map
    ctx.add_basemap(ax, crs=gdf.crs.to_string(),
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)

    # Set title
    ax.set_title('Flight Blocks', fontsize=16)

    # Show figure
    plt.show()


def plot_NDVI_map(gdf) -> None:
    """
    Plot NDVI map.
    :param gdf: GeoDataframe holding block data.
    """

    # Construct figure for visualization
    fig, ax = plt.subplots(1, 1)

    # Plot NDVI data cells
    gdf.plot(column='value', cmap='Greens', ax=ax, legend=True)

    # Add geographical reference map
    ctx.add_basemap(ax, crs=gdf.crs,
                    source=ctx.providers.OpenStreetMap.Mapnik, zoom=8)

    # Set title
    ax.set_title('NDVI Data cells', fontsize=16)

    # Show figure
    plt.show()
