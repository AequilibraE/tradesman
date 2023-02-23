import gc

import geopandas as gpd
from geopandas.tools import sjoin


def zones_with_population(project, zones_from_locations):
    """
    Saves hexbins with population into open project.

    Parameters:
         *project*(:obj:`aequilibrae.project`): current open project
         *zones_from_locations`(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing hexbins and their subdivision.
    """
    sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
    pop_data = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)

    pop_to_zone = sjoin(pop_data, zones_from_locations, how="right")
    pop_to_zone = pop_to_zone[["hex_id", "population"]]
    pop_to_zone.population.fillna(0, inplace=True)
    gc.collect()

    pop_per_zone = pop_to_zone.groupby(["hex_id"]).sum(numeric_only=True)[["population"]].reset_index()

    return zones_from_locations.merge(pop_per_zone, on="hex_id", how="left")
