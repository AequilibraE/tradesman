import geopandas as gpd


def subdivisions(project):
    """
    Returns the model's subdivisions.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    with project.db_connection as conn:
        sql = (
            "SELECT country_name, division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM political_subdivisions;"
        )
        return gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geom", crs=4326)
