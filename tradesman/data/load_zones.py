import geopandas as gpd
import sqlite3


def load_zones(project):
    """
    Returns the model's Traffic Analysis Zones.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    with project.db_connection as conn:
        sql = "SELECT zone_id, Hex(ST_AsBinary(GEOMETRY)) geometry FROM zones;"
        zones = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geometry", crs=4326)
    return zones
