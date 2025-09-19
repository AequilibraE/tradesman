import duckdb
import geopandas as gpd
from shapely import wkt


def get_subdivisions(project):
    """
    Returns the model's subdivisions.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    with duckdb.connect(project.project_base_path / "project_database.sqlite") as conn:
        conn.install_extension("spatial")
        conn.load_extension("spatial")

        sql = (
            "SELECT country_name, division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM political_subdivisions;"
        )
        subdivisions = conn.execute(sql).df()
        return gpd.GeoDataFrame(subdivisions, geometry=subdivisions["geom"].apply(wkt.loads), crs="EPSG:4326")
