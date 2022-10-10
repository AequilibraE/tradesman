import geopandas as gpd
from math import ceil, sqrt
from aequilibrae.project import Project


def bounding_boxes(project: Project, km_side=25):
    """
    Creates the bounding boxes to speed-up Overpass API query.

    Parameters:
         *project*(:obj:`aequilibrae.project): current project.
         *tile_size*(:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side.
    """

    sql_coverage = "SELECT Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where level=0;"

    coverage_area = gpd.GeoDataFrame.from_postgis(sql_coverage, project.conn, geom_col="geometry", crs=4326)

    parts = ceil(sqrt(coverage_area.to_crs(3857).area.sum() / (km_side * km_side * 1000 * 1000)))

    area_bounds = coverage_area.bounds.values[0]

    if parts == 1:
        bboxes = [[area_bounds[1], area_bounds[0], area_bounds[3], area_bounds[2]]]
    else:
        bboxes = []
        xmin, ymin, xmax, ymax = area_bounds
        ymin_global = ymin
        delta_x = (xmax - xmin) / parts
        delta_y = (ymax - ymin) / parts
        for i in range(parts):
            xmax = xmin + delta_x
            for j in range(parts):
                ymax = ymin + delta_y
                bboxes.append([ymin, xmin, ymax, xmax])
                ymin = ymax
            xmin = xmax
            ymin = ymin_global

    return bboxes
