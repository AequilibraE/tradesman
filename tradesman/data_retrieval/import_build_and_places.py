from os import mkdir
from os.path import dirname, isdir, join

import duckdb
import geopandas as gpd
import pandas as pd
from aequilibrae.project import Project
from shapely import wkt

from tradesman.utils import set_bbox


class ImportBuildPlaces:
    def __init__(self, project: Project, box_side: int = 25) -> None:
        self.project = project
        self.box_side = box_side

        self.__xmin = float(self.project.about.xmin)
        self.__xmax = float(self.project.about.xmax)
        self.__ymin = float(self.project.about.ymin)
        self.__ymax = float(self.project.about.ymax)

        zones = self.project.zoning.data.copy()
        self.zones = zones[["zone_id", "geometry"]]

    def building_parser(self, bbox, conn):
        qry = """
            SELECT
                id as ovm_id,
                sources[1].dataset as source_dataset,
                sources[1].record_id as source_id,
                subtype,
                class,
                ST_AsText(geometry) as geometry
            FROM
                read_parquet('s3://overturemaps-us-west-2/release/2025-07-23.0/theme=buildings/type=building/*')
            WHERE
                bbox.ymin >= {} AND
                bbox.xmin >= {} AND
                bbox.ymax <= {} AND
                bbox.xmax <= {};
            """
        qry = qry.format(*bbox)

        buildings = conn.execute(qry).df()
        buildings["subtype"] = buildings["subtype"].fillna("undetermined")
        buildings["class"] = buildings["class"].fillna("undetermined")

        return buildings

    def places_parser(self, bbox, conn):
        qry = """
        SELECT
            id as ovm_id,
            sources[1].dataset as source_dataset,
            sources[1].record_id as source_id,
            categories.primary as tags,
            categories.alternate as secondary_tags,
            ST_AsText(geometry) as geometry
        FROM
            read_parquet('s3://overturemaps-us-west-2/release/2025-07-23.0/theme=places/type=place/*')
        WHERE
            bbox.ymin >= {} AND
            bbox.xmin >= {} AND
            bbox.ymax <= {} AND
            bbox.xmax <= {};
        """
        qry = qry.format(*bbox)

        places = conn.execute(qry).df()

        # TODO: add a prepared file to be read as csv
        categories = pd.read_csv(join(dirname(__file__), "ovm_categories.csv"), sep=";")
        categories["main_category"] = (
            categories["taxonomy"].str.replace("[", "").str.replace("]", "").str.split(",", expand=True)[0]
        )
        categories.drop(["taxonomy"], axis=1, inplace=True)

        cols = ["ovm_id", "source_dataset", "source_id", "tags", "secondary_tags", "main_category", "geometry"]
        places = places.merge(categories, on="tags")
        places = places[cols]

        return places

    def import_building(self):
        con = duckdb.connect()
        con.install_extension("spatial")
        con.load_extension("spatial")

        bboxes = set_bbox(self.__xmin, self.__ymin, self.__xmax, self.__ymax, self.box_side)

        blds = []
        for bbox in bboxes:
            blds.append(self.building_parser(bbox, con))

        buildings = pd.concat(blds)
        buildings = gpd.GeoDataFrame(buildings, geometry=buildings["geometry"].apply(wkt.loads), crs="EPSG:4326")
        buildings = gpd.sjoin(buildings, self.zones)  # Join with the zones database
        buildings = buildings.drop_duplicates(["ovm_id"]).reset_index(drop=True)
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["ovm_id", "source_id", "source_dataset", "subtype", "class", "zone_id", "area", "geometry"]
        buildings = buildings[cols]

        if not isdir(self.project.project_base_path / "data_download"):
            mkdir(self.project.project_base_path / "data_download")
        buildings.to_parquet(self.project.project_base_path / "data_download" / "ovm_buildings.parquet")

        bld_count = buildings[["zone_id", "ovm_id"]].groupby("zone_id").count()
        bld_area = buildings[["zone_id", "area"]].groupby("zone_id").sum()

        with self.project.db_connection as conn:
            conn.execute("ALTER TABLE zones ADD ovm_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD ovm_bld_area FLOAT;")

            if not bld_count.empty:
                for zone_id, row in bld_count.iterrows():
                    count_qry = "UPDATE zones SET ovm_bld_count={} WHERE zone_id={}".format(row["ovm_id"], zone_id)
                    conn.execute(count_qry)

            if not bld_area.empty:
                for zone_id, row in bld_area.iterrows():
                    area_qry = "UPDATE zones SET ovm_bld_area={} WHERE zone_id={}".format(row["area"], zone_id)
                    conn.execute(area_qry)

            conn.execute("UPDATE zones SET ovm_bld_area=0, ovm_bld_count=0 WHERE ovm_bld_area IS NULL;")

    def import_places(self):
        con = duckdb.connect()
        con.install_extension("spatial")
        con.load_extension("spatial")

        bboxes = self.set_bbox()

        places = []
        for bbox in bboxes:
            places.append(self.places_parser(bbox, con))

        all_places = pd.concat(places)
        all_places = gpd.GeoDataFrame(all_places, geometry=all_places["geometry"].apply(wkt.loads), crs="EPSG:4326")
        all_places = gpd.sjoin(all_places, self.zones)
        all_places.reset_index(drop=True, inplace=True)

        cols = ["ovm_id", "source_id", "source_dataset", "main_category", "tags", "secondary_tags", "zone_id"]
        cols.extend("geometry")
        all_places = all_places[cols]

        if not isdir(self.project.project_base_path / "data_download"):
            mkdir(self.project.project_base_path / "data_download")
        all_places.to_parquet(self.project.project_base_path / "data_download" / "ovm_points_of_interest.parquet")

        poi_count = all_places[["ovm_id", "zone_id"]].groupby("zone_id").count()

        with self.project.db_connection as conn:
            conn.execute("ALTER TABLE zones ADD ovm_poi_count INT;")

            if not poi_count.empty:
                for zone_id, row in poi_count.iterrows():
                    count_qry = "UPDATE zones SET ovm_poi_count={} WHERE zone_id={}".format(row["ovm_id"], zone_id)
                    conn.execute(count_qry)

            conn.execute("UPDATE zones SET ovm_poi_count=0 WHERE ovm_poi_count IS NULL;")
