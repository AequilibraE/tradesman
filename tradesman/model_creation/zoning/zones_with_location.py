import geopandas as gpd
import pandas as pd
from geopandas.tools import sjoin


def zones_with_location(hexb, all_subdivisions):
    # Hexbins are incredibly small, so getting their centroids from 4326 is not an issue
    centroids = gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb.centroid, crs="EPSG:4326")

    states = all_subdivisions[all_subdivisions.level == all_subdivisions.level.max()]
    states.reset_index(drop=True, inplace=True)

    data = sjoin(centroids, states, how="left", predicate="intersects")  # replace district by state
    data.drop_duplicates(subset=["hex_id"], inplace=True)
    data = data[["hex_id", "division_name", "geometry"]]
    found_centroid = data[["hex_id", "division_name"]]
    found_centroid = found_centroid.dropna()

    not_found = hexb[~hexb.hex_id.isin(found_centroid.hex_id)]
    not_found_merged = sjoin(not_found, states, how="left", predicate="intersects")
    not_found_merged = not_found_merged[["hex_id", "division_name"]]
    not_found_merged.dropna(inplace=True)

    with_data = pd.concat([not_found_merged, found_centroid])

    data_complete = hexb.merge(with_data, on="hex_id", how="outer")

    dindex = states.sindex
    empties = data_complete.division_name.isna()

    for idx, record in data_complete[empties].iterrows():
        geo = record.geometry
        dscrt = [x for x in dindex.nearest(geo.bounds, 10)]
        dist = [states.loc[d, "geometry"].distance(geo) for d in dscrt]
        m = dscrt[dist.index(min(dist))]
        data_complete.loc[idx, "division_name"] = states.loc[m, "division_name"]

    zones_with_location = gpd.GeoDataFrame(data_complete[["hex_id", "division_name"]],
                                           geometry=data_complete["geometry"])

    return zones_with_location
