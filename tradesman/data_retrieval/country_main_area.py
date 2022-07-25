import shapely
from aequilibrae import Project
from shapely.geometry import MultiPolygon


def country_border_from_model(project: Project):
    country_wkb = project.conn.execute("Select asBinary(geometry) from political_subdivisions where level=0").fetchone()
    if not country_wkb:
        return MultiPolygon([])
    country_geo = shapely.wkb.loads(country_wkb[0])
    return country_geo
