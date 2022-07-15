import geopandas as gpd


def subdivisions(project):
    sql = "SELECT division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM country_subdivisions;"
    return gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)
