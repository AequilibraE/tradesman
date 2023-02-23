import geopandas as gpd


def load_vectorized_pop(project):
    """
    Returns the model's raw_population data.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
    return gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)
