import geopandas as gpd
import pandas as pd
from geopandas.tools import sjoin
from shapely.geometry import box
from tqdm import tqdm


def zones_with_location(hexb, all_subdivisions):
    """
    Identifies which political subdivision the hexbins belong to.
    Parameters:
         *hexb*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing all hexbins within the model area.
         *all_subdivisions*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing all political subdivisions.

    """
    # Hexbins are incredibly small, so getting their centroids from 4326 is not an issue
    centroids = gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb.centroid, crs="EPSG:4326")

    states = all_subdivisions[all_subdivisions.level == all_subdivisions.level.max()]
    states.reset_index(drop=True, inplace=True)

    data = gpd.sjoin_nearest(centroids, states, how="left")
    data = data[["hex_id", "division_name", "geometry"]]

    data_complete = hexb.merge(data, on="hex_id", how="outer")

    data_complete.drop_duplicates(subset=["hex_id"], inplace=True)

    return gpd.GeoDataFrame(data_complete[["hex_id", "division_name"]], geometry=data_complete["geometry_x"])
