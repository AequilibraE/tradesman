import geopandas as gpd


def load_vectorized_pop(project):
    sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
    return gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)
