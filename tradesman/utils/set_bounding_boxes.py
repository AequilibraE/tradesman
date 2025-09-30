from math import ceil, sqrt

import geopandas as gpd
from shapely import box


def set_bbox(xmin, ymin, xmax, ymax, box_side: int = 25):
    """Split the model area into different bounding boxes
    Will now return ['ymin', 'xmin', 'ymax', 'xmax']
    """
    bbox = box(xmin, ymin, xmax, ymax)

    geo = gpd.GeoDataFrame([1], columns=["fid"], geometry=[bbox], crs="EPSG:4326")
    area_bounds = geo.bounds.values.tolist()[0]
    parts = ceil(sqrt(geo.to_crs("EPSG:3857").area.sum() / (box_side * box_side * 1000 * 1000)))

    if parts == 1:
        return [[area_bounds[1], area_bounds[0], area_bounds[3], area_bounds[2]]]
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
