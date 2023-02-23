from aequilibrae.project import Project
from math import ceil, sqrt

import geopandas as gpd
import numpy as np
import pandas as pd

from tradesman.data_retrieval.country_main_area import model_borders


def bounding_boxes(project: Project, km_side=25):
    """
    Creates a bounding box for the model area.

    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project
         *km_side*(:obj:`int`): size of the box to be created

    """
    country = model_borders(project)

    geo_country = gpd.GeoDataFrame(
        pd.DataFrame(
            list(country.geoms),
            index=np.arange(len(country.geoms)),
            columns=["geometry"],
        ),
        geometry="geometry",
        crs=4326,
    )

    parts = ceil(sqrt(geo_country.to_crs(3857).area.sum() / (km_side * km_side * 1000 * 1000)))

    area_bounds = list(country.bounds)

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
