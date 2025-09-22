from aequilibrae import Project
from aequilibrae.utils.db_utils import commit_and_close
import shapely
from shapely.geometry import MultiPolygon


def country_border_from_model(project: Project):
    """
    Returns the model's country border.

    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project

    """
    db_path = project.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        country_wkb = conn.execute("Select asBinary(geometry) from political_subdivisions where level=0").fetchone()
    if not country_wkb:
        return MultiPolygon([])
    country_geo = shapely.wkb.loads(country_wkb[0])
    return country_geo


def model_borders(project: Project):
    """
    Returns the model area.

    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project

    """
    db_path = project.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        country_wkb = conn.execute("Select asBinary(geometry) from political_subdivisions where level=-1").fetchone()
    if not country_wkb:
        return MultiPolygon([])
    country_geo = shapely.wkb.loads(country_wkb[0])
    return country_geo
