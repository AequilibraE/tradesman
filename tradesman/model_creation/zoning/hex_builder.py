from math import floor
from time import perf_counter
import multiprocessing as mp

import geopandas as gpd
import numpy as np
import pandas as pd
import importlib.util as iutil
from shapely.geometry import Polygon
from tqdm import tqdm

has_dask_geopandas = iutil.find_spec("dask_geopandas") is not None


def hex_builder(coverage_area, hex_height, epsg=3857):
    """
    Creates hexbins that covers all project area.

    Parameters:
         *coverage_area*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing country borders
         *hex_height*(:obj:`int`): size of the hexbin size. Defaults to 200
         *epsg*(:obj:`int`): EPSG code specifying output projection. Defaults to 3857
    """
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
    threshold = 5_000_000
    tot_columns = int(floor(float(x_right - x_left) / x_spacing))
    tot_rows = int(floor(float(y_top - y_bottom) / hex_height))
    tot_elements = tot_columns * tot_rows
    print(f"Expect {tot_elements:,} total hexbins for this bounding box")

    def data_conversion(dt, ref_sys):
        df = pd.DataFrame(dt, columns=["hex_id", "x", "y", "geometry"])
        return gpd.GeoDataFrame(df[["hex_id", "x", "y"]], geometry=df["geometry"], crs=f"epsg:{ref_sys}")

    half_height = hex_height / 2
    vertex_diff = xvertexhi - xvertexlo
    for column in tqdm(range(tot_columns)):
        # (column + 1) and (row + 1) calculation is used to maintain
        # _topology between adjacent shapes and avoid overlaps/holes
        # due to rounding errors

        x1 = x_left + (column * x_spacing)  # far _left
        x2 = x1 + vertex_diff  # _left
        x3 = x_left + ((column + 1) * x_spacing)  # _right
        x4 = x3 + vertex_diff  # far _right
        xm = (x2 + x3) / 2
        col_setting = 0 if (column % 2) == 0 else 1
        for row in range(tot_rows):
            y1 = y_bottom + (((row * 2) + col_setting + 0) * half_height)  # hi
            y2 = y_bottom + (((row * 2) + col_setting + 1) * half_height)  # mid
            y3 = y_bottom + (((row * 2) + col_setting + 2) * half_height)  # lo

            poly = Polygon([(x1, y2), (x2, y1), (x3, y1), (x4, y2), (x3, y3), (x2, y3), (x1, y2)])
            data.append([poly_id, xm, y2, poly])
            poly_id += 1

            if poly_id % threshold == 0:
                print(f"{poly_id:,} --> ({round(perf_counter() - t, 1)} s)")
                t = perf_counter()
                results.append(data_conversion(data, epsg))
                data.clear()

    if data:
        results.append(data_conversion(data, epsg))
        data.clear()

    hexb = pd.concat(results)

    if has_dask_geopandas:
        import dask_geopandas

        ddf = dask_geopandas.from_geopandas(hexb, npartitions=5 * mp.cpu_count())
        ddf = ddf.clip(coverage_area.unary_union, keep_geom_type=True)
        hexb = gpd.GeoDataFrame(ddf)
        hexb.columns = ddf.columns

    else:
        hexb = hexb.clip(coverage_area.unary_union, keep_geom_type=True)

    hexb.hex_id = np.arange(hexb.shape[0]) + 1
    return gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb["geometry"], crs=f"epsg:{epsg}")
