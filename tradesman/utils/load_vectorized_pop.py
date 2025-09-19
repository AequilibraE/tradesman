import duckdb
import geopandas as gpd
from shapely import wkt


def load_vectorized_pop(project):
    """
    Returns the model's raw_population data.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    with duckdb.connect(project.project_base_path / "project_database.sqlite") as conn:
        conn.install_extension("spatial")
        conn.load_extension("spatial")

        sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
        population = conn.execute(sql).df()
        return gpd.GeoDataFrame(population, geometry=population["geom"].apply(wkt.loads), crs="EPSG:4326")
