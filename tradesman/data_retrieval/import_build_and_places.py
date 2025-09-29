from os import mkdir
from os.path import dirname, isdir, join

import geopandas as gpd
import pandas as pd
from aequilibrae.project import Project
from overturemaps import core

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

    def building_parser(self, bbox):
        buildings = core.geodataframe("building", bbox=bbox)
        buildings["source_dataset"] = [source[0]["dataset"] for source in buildings["sources"]]
        buildings["source_id"] = [source[0]["record_id"] for source in buildings["sources"]]
        buildings["subtype"] = buildings["subtype"].fillna("undetermined")
        buildings["class"] = buildings["class"].fillna("undetermined")

        return buildings[["id", "source_dataset", "source_id", "subtype", "class", "geometry"]]

    def places_parser(self, bbox):
        places = core.geodataframe("place", bbox=bbox)
        places["source_dataset"] = [source[0]["dataset"] for source in places["sources"]]
        places["source_id"] = [source[0]["record_id"] for source in places["sources"]]
        places["tags"] = [cat["primary"] for cat in places["categories"]]
        places["secondary_tags"] = [cat["alternate"] for cat in places["categories"]]

        categories = pd.read_csv(join(dirname(__file__), "ovm_tags/ovm_categories.csv"), sep=",")

        places = places.merge(categories, on="tags")

        return places[["id", "source_dataset", "source_id", "tags", "secondary_tags", "main_category", "geometry"]]

    def import_buildings(self):
        bboxes = set_bbox(self.__xmin, self.__ymin, self.__xmax, self.__ymax, self.box_side, True)

        blds = []
        for bbox in bboxes:
            blds.append(self.building_parser(bbox))

        buildings = pd.concat(blds)
        buildings = buildings.set_crs(crs="WGS84")  # GeoJSON default is WGS84
        buildings = gpd.sjoin(buildings, self.zones)  # Join with the zones database
        buildings = buildings.drop_duplicates(["id"]).reset_index(drop=True)
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["id", "source_id", "source_dataset", "subtype", "class", "zone_id", "area", "geometry"]
        buildings = buildings[cols]

        if not isdir(self.project.project_base_path / "ovm_data"):
            mkdir(self.project.project_base_path / "ovm_data")
        buildings.to_parquet(self.project.project_base_path / "ovm_data" / "ovm_buildings.parquet")

        bld_count = buildings[["zone_id", "id"]].groupby("zone_id").count()
        bld_area = buildings[["zone_id", "area"]].groupby("zone_id").sum()

        with self.project.db_connection as conn:
            conn.execute("ALTER TABLE zones ADD ovm_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD ovm_bld_area FLOAT;")

            if not bld_count.empty:
                for zone_id, row in bld_count.iterrows():
                    count_qry = "UPDATE zones SET ovm_bld_count={} WHERE zone_id={}".format(row["id"], zone_id)
                    conn.execute(count_qry)

            if not bld_area.empty:
                for zone_id, row in bld_area.iterrows():
                    area_qry = "UPDATE zones SET ovm_bld_area={} WHERE zone_id={}".format(row["area"], zone_id)
                    conn.execute(area_qry)

            conn.execute("UPDATE zones SET ovm_bld_area=0, ovm_bld_count=0 WHERE ovm_bld_area IS NULL;")

    def import_places(self):
        bboxes = set_bbox(self.__xmin, self.__ymin, self.__xmax, self.__ymax, self.box_side, True)

        places = []
        for bbox in bboxes:
            places.append(self.places_parser(bbox))

        all_places = pd.concat(places)
        all_places = all_places.set_crs(crs="WGS84")  # GeoJSON default is WGS84
        all_places = gpd.sjoin(all_places, self.zones)
        all_places.reset_index(drop=True, inplace=True)

        cols = ["id", "source_id", "source_dataset", "main_category", "tags", "secondary_tags", "zone_id", "geometry"]
        all_places = all_places[cols]

        if not isdir(self.project.project_base_path / "ovm_data"):
            mkdir(self.project.project_base_path / "ovm_data")
        all_places.to_parquet(self.project.project_base_path / "ovm_data" / "ovm_points_of_interest.parquet")

        poi_count = all_places[["id", "zone_id"]].groupby("zone_id").count()

        with self.project.db_connection as conn:
            conn.execute("ALTER TABLE zones ADD ovm_poi_count INT;")

            if not poi_count.empty:
                for zone_id, row in poi_count.iterrows():
                    count_qry = "UPDATE zones SET ovm_poi_count={} WHERE zone_id={}".format(row["id"], zone_id)
                    conn.execute(count_qry)

            conn.execute("UPDATE zones SET ovm_poi_count=0 WHERE ovm_poi_count IS NULL;")
