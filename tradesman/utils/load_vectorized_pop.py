import geopandas as gpd

from aequilibrae.utils.db_utils import commit_and_close


def load_vectorized_pop(project):
    """
    Returns the model's raw_population data.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    db_path = project.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
        return gpd.read_postgis(sql, conn, geom_col="geom", crs=4326)
