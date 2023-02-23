import geopandas as gpd
import sqlite3


def load_zones(project):
    """
    Returns the model's Traffic Analysis Zones.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    sql = "SELECT zone_id, Hex(ST_AsBinary(GEOMETRY)) geometry FROM zones;"
    zones = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geometry", crs=4326)
    return zones
