import geopandas as gpd

from aequilibrae.utils.db_utils import commit_and_close


def get_subdivisions(project):
    """
    Returns the model's subdivisions.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    db_path = project.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        sql = (
            "SELECT country_name, division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM political_subdivisions;"
        )
        return gpd.read_postgis(sql, conn, geom_col="geom", crs=4326)
