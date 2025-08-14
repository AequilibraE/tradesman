from aequilibrae.project import Project

from math import floor
from time import perf_counter
import multiprocessing as mp

import geopandas as gpd
import numpy as np
import pandas as pd
import importlib.util as iutil
from shapely.geometry import Polygon
from tqdm import tqdm
import gc

import warnings
from math import sqrt, ceil

import libpysal
from sklearn.cluster import KMeans
from shapely.geometry import box

has_dask_geopandas = iutil.find_spec("dask_geopandas") is not None


class ZoneBuilder:
    def __init__(
        self,
        project: Project,
        hexbin_size: int = 200,
        max_zone_pop: int = 10_000,
        min_zone_pop: int = 500,
        save_hexbins: bool = False,
    ) -> None:
        """
        Build Traffic Analysis Zones.

        Parameters:
            *project*(:obj:`aequilibrae.project`): currently open project

            *hexbin_size*(:obj:`int`): size of the hexbin size. Defaults to 200

            *max_zone_pop*(:obj:`int`): max population within a zone. Defaults to 10,000

            *min_zone_pop*(:obj:`int`): min population within a zone. Defaults to 500

            *save_hexbins*(:obj:`bool`): saves hexbins with population. Defaults to False
        """

        self.project = project
        self.hexbin_size = hexbin_size
        self.max_zone_pop = max_zone_pop
        self.min_zone_pop = min_zone_pop
        self.save_hexbins = save_hexbins

    @property
    def load_subdivisions(self):
        with self.project.db_connection as conn:
            sql = "SELECT division_name, level, Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions;"
            return gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geometry", crs="EPSG:4326")

    def hex_builder(self, epsg: int = 3857):
        """
        Creates hexbins that covers all project area.

        Parameters:
            *epsg*(:obj:`int`): EPSG code specifying output projection. Defaults to 3857.
        """
        # Function adapted from http://michaelminn.com/linux/mmqgis/

        coverage_area = self.load_subdivisions
        coverage_area = coverage_area[coverage_area.level == -1]
        coverage_area = coverage_area.explode(index_parts=True).reset_index(drop=True).to_crs("EPSG:3857")

        x_left, y_bottom, x_right, y_top = coverage_area.union_all().bounds

        results = []
        data = []
        # To preserve symmetry, hspacing is fixed relative to vspacing
        xvertexlo = 0.288675134594813 * self.hexbin_size
        xvertexhi = 0.577350269189626 * self.hexbin_size
        x_spacing = xvertexlo + xvertexhi

        poly_id = 1
        t = perf_counter()
        threshold = 5_000_000
        tot_columns = int(floor(float(x_right - x_left) / x_spacing))
        tot_rows = int(floor(float(y_top - y_bottom) / self.hexbin_size))
        tot_elements = tot_columns * tot_rows
        print(f"Expect {tot_elements:,} total hexbins for this bounding box")

        def data_conversion(dt, ref_sys):
            df = pd.DataFrame(dt, columns=["hex_id", "x", "y", "geometry"])
            return gpd.GeoDataFrame(df[["hex_id", "x", "y"]], geometry=df["geometry"], crs=f"EPSG:{ref_sys}")

        half_height = self.hexbin_size / 2
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
            ddf = ddf.clip(coverage_area.union_all(), keep_geom_type=True)
            hexb = gpd.GeoDataFrame(ddf)
            hexb.columns = ddf.columns

        else:
            hexb = hexb.clip(coverage_area.union_all(), keep_geom_type=True)

        hexb.hex_id = np.arange(hexb.shape[0]) + 1
        hexb = gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb["geometry"], crs=f"EPSG:{epsg}")
        return hexb.to_crs("EPSG:4326", inplace=True)

    def zones_with_location(self):
        """
        Identifies which political subdivision the hexbins belongs to.
        """
        hexb = self.hex_builder()

        # Hexbins are incredibly small, so getting their centroids from 4326 is not an issue
        centroids = gpd.GeoDataFrame(hexb[["hex_id"]], geometry=hexb.centroid, crs="EPSG:4326")

        subdivisions = self.load_subdivisions
        subdivisions = subdivisions[subdivisions.level == subdivisions.level.max()]

        if has_dask_geopandas:
            import dask_geopandas

            ddf = dask_geopandas.from_geopandas(centroids, npartitions=5 * mp.cpu_count())
            ddf.spatial_shuffle()
            ddf = dask_geopandas.sjoin(ddf, subdivisions, how="inner")

            data = gpd.GeoDataFrame(ddf)
            data.columns = ddf.columns
            data.drop_duplicates(subset=["hex_id"], inplace=True)
            found_centroid = data[["hex_id", "division_name"]]
            not_found = hexb[~hexb.hex_id.isin(found_centroid.hex_id)]
            not_found_merged = gpd.sjoin_nearest(not_found, subdivisions, how="left")
            not_found_merged = not_found_merged[["hex_id", "division_name"]]
            with_data = pd.concat([not_found_merged, found_centroid])
            data_complete = hexb.merge(with_data, on="hex_id", how="outer")
            geom_colum = "geometry"
        else:
            data = gpd.sjoin_nearest(centroids, subdivisions, how="left")
            data = data[["hex_id", "division_name", "geometry"]]
            data_complete = hexb.merge(data, on="hex_id", how="outer")
            data_complete.drop_duplicates(subset=["hex_id"], inplace=True)
            geom_colum = "geometry_x"

        gdf = gpd.GeoDataFrame(data_complete[["hex_id", "division_name"]], geometry=data_complete[geom_colum])
        gdf = gdf.explode(index_parts=True).drop_duplicates().reset_index(drop=True)
        gdf["hex_id"] = np.arange(1, len(gdf) + 1)

        return gdf

    def zones_with_population(self):
        """
        Saves hexbins with population into open project.
        """
        zones_from_locations = self.zones_with_location()

        with self.project.db_connection as conn:
            sql = "SELECT population, Hex(ST_AsBinary(GEOMETRY)) as geom FROM raw_population;"
            pop_data = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geom", crs=4326)

        pop_to_zone = gpd.sjoin(pop_data, zones_from_locations, how="right")
        pop_to_zone = pop_to_zone[["hex_id", "population"]]
        pop_to_zone.population.fillna(0, inplace=True)
        gc.collect()

        pop_per_zone = pop_to_zone.groupby(["hex_id"]).sum(numeric_only=True)[["population"]].reset_index()
        pop_per_zone = zones_from_locations.merge(pop_per_zone, on="hex_id", how="left")

        if self.save_hexbins:
            self.saves_hex_pop_to_file(pop_per_zone)

        return pop_per_zone

    def saves_hex_pop_to_file(self, gdf):
        """
        Saves hexbins with population into open project.

        Parameters:
            *gdf`(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing zones with population
        """
        pop_per_zone = gdf.copy()
        pop_per_zone["geo_wkt"] = pop_per_zone.geometry.to_wkt()
        pop_per_zone = pop_per_zone[pop_per_zone[["hex_id", "division_name", "population", "geo_wkt"]]]

        with self.project.db_connection as conn:
            pop_per_zone.to_sql("hex_pop", conn, if_exists="append", index=False)
            conn.execute("UPDATE hex_pop SET geometry=CastToMulti(GeomFromText(geo_wkt, 4326));")
            conn.execute("UPDATE hex_pop SET geo_wkt=NULL")
        del pop_per_zone

    def create_clusters(self, hexbins):
        """
        Creates population clusters by state.

        Parameters:
            *hexbins*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing hexbins and population info
        """

        if hexbins.population.max() > self.max_zone_pop:
            raise ValueError(
                """There is at least one hexbin with population greater than max_zone_pop.
            Plase change the parameter value."""
            )
        hexbins["zone_id"] = -1
        centroids = hexbins.geometry.centroid
        hexbins = hexbins.assign(x=centroids.x.values, y=centroids.y.values)
        list_states = list(hexbins.division_name.unique())
        data_store = []
        master_zone_id = 1
        result_col_df = ["hex_id", "x", "y", "population", "division_name", "zone_id"]
        for i, division_name in enumerate(list_states):
            df = hexbins[hexbins.division_name == division_name].copy()
            df.loc[:, "zone_id"] = master_zone_id + i
            data_store.append(df[result_col_df])

        for cnt, df in tqdm(enumerate(data_store)):
            t = df.groupby(["zone_id"]).sum(numeric_only=True)
            t = t.loc[t.population > self.max_zone_pop]
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
                if zone_pop < self.max_zone_pop:
                    continue
                fltr = df.zone_id == zone_to_analyze
                segments = max(2, ceil(sqrt(zone_pop / self.max_zone_pop)))
                prov_pop = df.loc[fltr, :]
                segments = min(prov_pop.shape[0], segments)
                if prov_pop.shape[0] < 2:
                    continue

                kmeans = KMeans(n_clusters=segments, random_state=0, n_init="auto")
                centr_results = kmeans.fit_predict(
                    X=prov_pop[["x", "y"]].values, sample_weight=prov_pop.population.values
                )
                df.loc[fltr, "zone_id"] = centr_results[:] + master_zone_id

                t = df.groupby(["zone_id"]).sum(numeric_only=True)
                ready = t.loc[t.population <= self.max_zone_pop].shape[0]
                avg = int(np.nansum(t.loc[t.population <= self.max_zone_pop, "population"]) / max(1, ready))
                t = t.loc[t.population > self.max_zone_pop]
                zone_sizes = t["population"].to_dict()
                zones_to_break = len(zone_sizes)
                master_zone_id += segments + 1
                if counter % 50 == 0:
                    print(f"Queue for analysis: {zones_to_break} (Done: {ready} ({avg} people/zone))")

        df = pd.concat(data_store)[["hex_id", "zone_id"]]
        cols_df = ["hex_id", "x", "y", "population", "division_name", "geometry"]
        df = pd.merge(hexbins[cols_df], df, on="hex_id")
        df = gpd.GeoDataFrame(df[result_col_df], geometry=df["geometry"])

        zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
        pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum(numeric_only=True)["population"]
        zoning = zoning.join(pop_total)

        exceptions = 0
        counter = zoning[zoning.geometry.type == "MultiPolygon"].shape[0]
        while counter > exceptions:
            for zid, record in zoning[zoning.geometry.type == "MultiPolygon"].iterrows():
                zone_df = df[df.zone_id == zid]
                with warnings.catch_warnings():
                    adj_mtx = libpysal.weights.Queen.from_dataframe(zone_df)
                islands = np.unique(adj_mtx.component_labels)
                island_pop = {isl: zone_df[adj_mtx.component_labels == isl].population.sum() for isl in islands}
                max_island = max(island_pop.values())
                remove_islands = [k for k, v in island_pop.items() if v < max_island]
                # failed = 0
                if len(remove_islands) == 0:
                    counter -= 1
                    continue
                for rmv in remove_islands:
                    island_hexbins = zone_df[adj_mtx.component_labels == rmv].hex_id
                    if zone_df[df.hex_id.isin(island_hexbins)].population.sum() > self.min_zone_pop:
                        df.loc[df.hex_id.isin(island_hexbins), "zone_id"] = master_zone_id
                        master_zone_id += 1
                        continue

                    closeby = []
                    for island_geo in zone_df[adj_mtx.component_labels == rmv].geometry.values:
                        closeby.extend(list(df.sindex.nearest(box(*island_geo.bounds))[1]))
                    closeby = list(set(closeby))
                    if not closeby:
                        # failed = 1
                        continue
                    adjacent = df.loc[df.index.isin(closeby), :]
                    available = [x for x in adjacent.zone_id.unique() if x != zid]
                    if not available:
                        # failed = 1
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
                # exceptions += failed
                counter -= 1

            zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
            pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum(numeric_only=True)["population"]
            zoning = zoning.join(pop_total)

        zoning = df.dissolve(by="zone_id")[["division_name", "geometry"]]
        pop_total = df[["zone_id", "population"]].groupby(["zone_id"]).sum(numeric_only=True)["population"]
        zoning = zoning.join(pop_total)

        zoning = zoning.reset_index(drop=True)
        zoning.index += 1

        return zoning

    def execute(self):
        with self.project.db_connection as conn:
            sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='hex_pop';"
            if sum(conn.execute(sql).fetchone()) > 0:
                conn.execute("DELETE FROM hex_pop;")
            conn.execute("DELETE FROM zones;")

        zones_with_pop = self.zones_with_population()

        clusters = self.create_clusters(zones_with_pop)

        with self.project.db_connection as conn:
            max_zone = clusters.index.max()

            min_node = conn.execute("Select min(node_id) from nodes").fetchone()[0]

            if min_node <= max_zone:
                increment = conn.execute("Select max(node_id) from nodes").fetchone()[0] + 1
                conn.execute("update nodes set node_id =node_id + ?", [increment])

        zoning = self.project.zoning
        for zone_id, row in clusters.iterrows():
            zone = zoning.new(zone_id)
            zone.geometry = row.geometry
            zone.population = row.population
            zone.save()
