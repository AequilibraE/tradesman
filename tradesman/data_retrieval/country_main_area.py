from aequilibrae import Project
import shapely


def get_main_area(project: Project):

    country_wkb = project.conn.execute("Select asBinary(geometry) from country_borders").fetchone()[0]
    country_geo = shapely.wkb.loads(country_wkb)
    return country_geo
