from geopandas import GeoDataFrame

from aequilibrae.project import Project


def load_zones(project: Project) -> GeoDataFrame:
    """
    Returns the model's Traffic Analysis Zones.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    with project.db_connection as conn:
        sql = "SELECT zone_id, Hex(ST_AsBinary(GEOMETRY)) geometry FROM zones;"
        return GeoDataFrame.from_postgis(sql, conn, geom_col="geometry", crs=4326)
