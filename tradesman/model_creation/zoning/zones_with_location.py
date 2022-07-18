import geopandas as gpd
import pandas as pd
from geopandas.tools import sjoin


def zones_with_location(hexb, all_subdivisions):
    centroids = gpd.GeoDataFrame(
        hexb[["hex_id"]],
        geometry=gpd.points_from_xy(hexb["x"], hexb["y"]),
        crs="EPSG:3405",
    )
    centroids.to_crs(4326, inplace=True)

    states = all_subdivisions[all_subdivisions.level == all_subdivisions.level.max()]

    data = sjoin(centroids, states, how="left", predicate="intersects")  # replace district by state
    data.drop_duplicates(subset=["hex_id"], inplace=True)
    data = data[["hex_id", "division_name", "geometry"]]  # remove district
    found_centroid = data[["hex_id", "division_name"]]  # remove district
    found_centroid = found_centroid.dropna()

    not_found = hexb[~hexb.hex_id.isin(found_centroid.hex_id)]
    # replace district by state
    not_found_merged = sjoin(not_found, states, how="left", predicate="intersects")
    not_found_merged = not_found_merged[["hex_id", "division_name_left"]]  # replace district
    not_found_merged.dropna(inplace=True)
    not_found_merged = not_found_merged.rename(columns={"division_name_left": "division_name"})

    with_data = pd.concat([not_found_merged, found_centroid])

    data_complete = hexb.merge(with_data, on="hex_id", how="outer")

    dindex = states.sindex
    empties = data_complete.division_name_x.isna()
    for idx, record in data_complete[empties].iterrows():
        geo = record.geometry
        dscrt = [x for x in dindex.nearest(geo.bounds, 10)]
        dist = [states.loc[d, "geometry"].distance(geo) for d in dscrt]
        m = dscrt[dist.index(min(dist))]
        data_complete.loc[idx, "division_name"] = states.loc[m, "division_name"]

    zones_with_location = gpd.GeoDataFrame(
        data_complete[["hex_id", "division_name_x", "x", "y"]],
        geometry=data_complete["geometry"],
    ).rename(columns={"division_name_x": "division_name"})

    return zones_with_location
