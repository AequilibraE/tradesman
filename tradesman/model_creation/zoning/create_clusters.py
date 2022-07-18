import warnings
from math import sqrt, ceil

import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def create_clusters(hexbins, max_zone_pop=10000, min_zone_pop=500):
    """
    This function creates population clusters by state.
    """

    hexbins["zone_id"] = -1
    list_states = list(hexbins.division_name.unique())
    data_store = []
    master_zone_id = 1
    for i, division_name in enumerate(list_states):
        df = hexbins[hexbins.division_name == division_name].copy()
        df.loc[:, "zone_id"] = master_zone_id + i
        data_store.append(df[["hex_id", "x", "y", "population", "division_name", "zone_id"]])

    for cnt, df in enumerate(data_store):
        t = df.groupby(["zone_id"]).sum()
        t = t.loc[t.population > max_zone_pop]
        zone_sizes = t["population"].to_dict()
        zones_to_break = len(zone_sizes)
        counter = 0
        if cnt % 25 == 0:
            print(f"Done {cnt}/{len(data_store)} states")
        while zones_to_break > 0:
            counter += 1
            zone_to_analyze = min(zone_sizes)
            zone_pop = zone_sizes.pop(zone_to_analyze)
            zones_to_break -= 1
            if zone_pop < max_zone_pop:
                continue
            fltr = df.zone_id == zone_to_analyze
            segments = max(2, ceil(sqrt(zone_pop / max_zone_pop)))
            prov_pop = df.loc[fltr, :]
            segments = min(prov_pop.shape[0], segments)
            if prov_pop.shape[0] < 2:
                continue

            kmeans = KMeans(n_clusters=segments, random_state=0)
            centr_results = kmeans.fit_predict(X=prov_pop[["x", "y"]].values, sample_weight=prov_pop.population.values)
            df.loc[fltr, "zone_id"] = centr_results[:] + master_zone_id

            t = df.groupby(["zone_id"]).sum()
            ready = t.loc[t.population <= max_zone_pop].shape[0]
            avg = int(np.nansum(t.loc[t.population <= max_zone_pop, "population"]) / max(1, ready))
            t = t.loc[t.population > max_zone_pop]
            zone_sizes = t["population"].to_dict()
            zones_to_break = len(zone_sizes)
            master_zone_id += segments + 1
            if counter % 50 == 0:
                print(f"Queue for analysis: {zones_to_break} (Done: {ready} ({avg} people/zone))")

    df = pd.concat(data_store)[["hex_id", "zone_id"]]
    df = pd.merge(
        hexbins[["hex_id", "x", "y", "population", "division_name", "geometry"]],
        df,
        on="hex_id",
    )
    df = gpd.GeoDataFrame(
        df[["hex_id", "x", "y", "population", "division_name", "zone_id"]],
        geometry=df["geometry"],
    )

    zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
    pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum()["population"]
    zoning = zoning.join(pop_total)

    exceptions = 0
    while zoning[zoning.geometry.type == "MultiPolygon"].shape[0] > exceptions:
        print(1)
        for zid, record in zoning[zoning.geometry.type == "MultiPolygon"].iterrows():
            zone_df = df[df.zone_id == zid]
            with warnings.catch_warnings():
                adj_mtx = libpysal.weights.Queen.from_dataframe(zone_df)
            islands = np.unique(adj_mtx.component_labels)
            island_pop = {isl: zone_df[adj_mtx.component_labels == isl].population.sum() for isl in islands}
            max_island = max(island_pop.values())
            remove_islands = [k for k, v in island_pop.items() if v < max_island]
            failed = 0
            for rmv in remove_islands:
                island_hexbins = zone_df[adj_mtx.component_labels == rmv].hex_id
                if zone_df[df.hex_id.isin(island_hexbins)].population.sum() > min_zone_pop:
                    df.loc[df.hex_id.isin(island_hexbins), "zone_id"] = master_zone_id
                    master_zone_id += 1
                    continue

                closeby = []
                for island_geo in zone_df[adj_mtx.component_labels == rmv].geometry.values:
                    closeby.extend([x[1] for x in df.sindex.nearest(island_geo, 6)])
                closeby = list(set(list(closeby)))
                if not closeby:
                    failed = 1
                    continue
                adjacent = df.loc[df.index.isin(closeby), :]
                available = [x for x in adjacent.zone_id.unique() if x != zid]
                if not available:
                    failed = 1
                    continue

                same_area = [
                    av
                    for av in available
                    if adjacent.loc[adjacent.zone_id == av, "division_name"].values[0] == record.division_name
                ]
                if same_area:
                    df.loc[df.hex_id.isin(island_hexbins), "zone_id"] = same_area[0]
                else:
                    counts = adjacent[adjacent.zone_id != zid].groupby(["zone_id"]).count()
                    counts = list(counts[counts.hex_id == counts.hex_id.max()].index)[0]

                    df.loc[df.hex_id.isin(island_hexbins), "division_name"] = adjacent.loc[
                        adjacent.zone_id == counts, "division_name"
                    ].values[0]
                    df.loc[df.hex_id.isin(island_hexbins), "zone_id"] = counts
            exceptions += failed

        zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
        pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum()["population"]
        zoning = zoning.join(pop_total)

    zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
    pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum()["population"]
    zoning = zoning.join(pop_total)

    zoning = zoning.reset_index(drop=True)
    zoning.index += 1

    return zoning
