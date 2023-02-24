import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas.tools import sjoin
from shapely.geometry import box
from tqdm import tqdm
import importlib.util as iutil
import multiprocessing as mp

has_dask_geopandas = iutil.find_spec("dask_geopandas") is not None


def zones_with_location(hexb, states):
    """
    Identifies which political subdivision the hexbins belong to.

    Parameters:
         *hexb*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing all hexbins within the model area.
         *states*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing all political divisions at the lowest level available.

    """
    # Hexbins are incredibly small, so getting their centroids from 4326 is not an issue
    centroids = gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb.centroid, crs="EPSG:4326")

    if has_dask_geopandas:
        import dask_geopandas

        ddf = dask_geopandas.from_geopandas(centroids, npartitions=5 * mp.cpu_count())
        ddf.spatial_shuffle()
        ddf = dask_geopandas.sjoin(ddf, states, how="inner")

        data = gpd.GeoDataFrame(ddf)
        data.columns = ddf.columns
        data.drop_duplicates(subset=["hex_id"], inplace=True)
        found_centroid = data[["hex_id", "division_name"]]
        not_found = hexb[~hexb.hex_id.isin(found_centroid.hex_id)]
        not_found_merged = gpd.sjoin_nearest(not_found, states, how="left")
        not_found_merged = not_found_merged[["hex_id", "division_name"]]
        with_data = pd.concat([not_found_merged, found_centroid])
        data_complete = hexb.merge(with_data, on="hex_id", how="outer")
        geom_colum = "geometry"
    else:
        data = gpd.sjoin_nearest(centroids, states, how="left")
        data = data[["hex_id", "division_name", "geometry"]]
        data_complete = hexb.merge(data, on="hex_id", how="outer")
        data_complete.drop_duplicates(subset=["hex_id"], inplace=True)
        geom_colum = "geometry_x"

    gdf = gpd.GeoDataFrame(data_complete[["hex_id", "division_name"]], geometry=data_complete[geom_colum])

    gdf = gdf.explode(index_parts=True).drop_duplicates()

    gdf.reset_index(drop=True, inplace=True)

    gdf["hex_id"] = np.arange(1, len(gdf) + 1)

    return gdf
