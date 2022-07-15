from math import floor
from time import perf_counter

import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas.tools import sjoin
from shapely.geometry import Polygon


def hex_builder(coverage_area, hex_height, epsg=3857):
    # Function adapted from http://michaelminn.com/linux/mmqgis/

    x_left, y_bottom, x_right, y_top = coverage_area.unary_union.bounds

    results = []
    data = []
    # To preserve symmetry, hspacing is fixed relative to vspacing
    xvertexlo = 0.288675134594813 * hex_height
    xvertexhi = 0.577350269189626 * hex_height
    x_spacing = xvertexlo + xvertexhi

    poly_id = 1
    t = perf_counter()
    threshold = 5000000
    tot_elements = int(floor(float(x_right - x_left) / x_spacing)) * int(floor(float(y_top - y_bottom) / hex_height))
    print(f"Expect {tot_elements:,} total hexbins for this bounding box")

    def data_conversion(dt, ref_sys, area):
        df = pd.DataFrame(dt)
        df.columns = ["hex_id", "x", "y", "geometry"]
        df = gpd.GeoDataFrame(df[["hex_id", "x", "y"]], geometry=df["geometry"])
        df.set_crs(f"epsg:{ref_sys}", inplace=True)

        if area is not None:
            df = sjoin(df, area, how="left", predicate="intersects")
            df = df[~df.index_right.isna()]
            df.drop(["index_right"], axis=1, inplace=True)
        return df

    for column in range(0, int(floor(float(x_right - x_left) / x_spacing))):
        # (column + 1) and (row + 1) calculation is used to maintain
        # _topology between adjacent shapes and avoid overlaps/holes
        # due to rounding errors

        x1 = x_left + (column * x_spacing)  # far _left
        x2 = x1 + (xvertexhi - xvertexlo)  # _left
        x3 = x_left + ((column + 1) * x_spacing)  # _right
        x4 = x3 + (xvertexhi - xvertexlo)  # far _right
        xm = (x2 + x3) / 2

        for row in range(0, int(floor(float(y_top - y_bottom) / hex_height))):
            if (column % 2) == 0:
                y1 = y_bottom + (((row * 2) + 0) * (hex_height / 2))  # hi
                y2 = y_bottom + (((row * 2) + 1) * (hex_height / 2))  # mid
                y3 = y_bottom + (((row * 2) + 2) * (hex_height / 2))  # lo
            else:
                y1 = y_bottom + (((row * 2) + 1) * (hex_height / 2))  # hi
                y2 = y_bottom + (((row * 2) + 2) * (hex_height / 2))  # mid
                y3 = y_bottom + (((row * 2) + 3) * (hex_height / 2))  # lo

            poly = Polygon([(x1, y2), (x2, y1), (x3, y1), (x4, y2), (x3, y3), (x2, y3), (x1, y2)])
            data.append([poly_id, xm, y2, poly])
            poly_id += 1

            if poly_id % threshold == 0:
                print(
                    f"{poly_id:,} --> ({round(perf_counter() - t, 1)} s)",
                )
                t = perf_counter()
                results.append(data_conversion(data, epsg, coverage_area))
                data.clear()

    if data:
        results.append(data_conversion(data, epsg, coverage_area))
        data.clear()

    df = pd.concat(results)
    df.loc[:, "hex_id"] = np.arange(df.shape[0]) + 1

    return df
