from os.path import dirname, join
from math import ceil, sqrt
import geopandas as gpd
import pandas as pd
import duckdb
from aequilibrae.project import Project
from shapely import box, wkt


class ImportBuildPlaces:
    def __init__(self, project: Project, box_side: int = 25) -> None:
        self.project = project
        self.box_side = box_side

        self.__xmin = float(self.project.about.xmin)
        self.__xmax = float(self.project.about.xmax)
        self.__ymin = float(self.project.about.ymin)
        self.__ymax = float(self.project.about.ymax)

        self.con = duckdb.connect()
        self.con.install_extension("spatial")
        self.con.load_extension("spatial")

        self.bboxes = self.set_bbox()

    def set_bbox(self):
        """Split the model area into different bounding boxes
        Will now return ['xmin', 'ymin', 'xmax', 'ymax']
        """
        bbox = box(self.__xmin, self.__ymin, self.__xmax, self.__ymax)

        geo = gpd.GeoDataFrame([1], columns=["fid"], geometry=[bbox], crs="EPSG:4326")
        area_bounds = geo.bounds.values.tolist()
        parts = ceil(sqrt(geo.to_crs("EPSG:3857").area.sum() / (self.box_side * self.box_side * 1000 * 1000)))

        if parts == 1:
            return area_bounds
        else:
            bboxes = []
            xmin, ymin, xmax, ymax = area_bounds[0]
            ymin_global = ymin
            delta_x = (xmax - xmin) / parts
            delta_y = (ymax - ymin) / parts
            for i in range(parts):
                xmax = xmin + delta_x
                for j in range(parts):
                    ymax = ymin + delta_y
                    bboxes.append([xmin, ymin, xmax, ymax])
                    ymin = ymax
                xmin = xmax
                ymin = ymin_global

            return bboxes

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
                bbox.xmin >= {} AND 
                bbox.ymin >= {} AND 
                bbox.xmax <= {} AND
                bbox.ymax <= {};
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
            categories.primary as main_ovm_tags,
            categories.alternate as secondary_ovm_tags,
            ST_AsText(geometry) as geometry
        FROM
            read_parquet('s3://overturemaps-us-west-2/release/2025-07-23.0/theme=places/type=place/*')
        WHERE
            bbox.xmin >= {} AND 
            bbox.ymin >= {} AND 
            bbox.xmax <= {} AND
            bbox.ymax <= {};
        """
        qry = qry.format(*bbox)

        places = conn.execute(qry).df()
        places = gpd.GeoDataFrame(places, geometry=places["geometry"].apply(wkt.loads), crs="EPSG:4326")

        # TODO: add a prepared file to be read as csv
        categories = pd.read_csv(join(dirname(__file__), "ovm_categories.csv"), sep=";")
        categories["main_category"] = (
            categories["taxonomy"].str.replace("[", "").str.replace("]", "").str.split(",", expand=True)[0]
        )
        categories.drop(["taxonomy"], axis=1, inplace=True)

        cols = ["ovm_id", "source_dataset", "source_id", "main_ovm_tags", "secondary_ovm_tags", "main_category"]
        cols.extend("geometry")
        places = places.merge(categories, on="tags")
        places = places[cols]

        return places

    def import_building(self):
        blds = []
        for bbox in self.bboxes:
            blds.append(self.building_parser(bbox, self.con))

        zones = self.project.zoning.data.copy()
        zones = zones[["zone_id", "geometry"]]

        buildings = pd.concat(blds)
        buildings = gpd.GeoDataFrame(buildings, geometry=buildings["geometry"].apply(wkt.loads), crs="EPSG:4326")
        buildings = gpd.sjoin(buildings, zones)  # Join with the zones database
        buildings = buildings.drop_duplicates(["ovm_id"]).reset_index(drop=True)
        buildings["geom"] = buildings.geometry.to_wkb()
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["ovm_id", "source_id", "source_dataset", "subtype", "class", "zone_id", "area", "geom"]
        buildings = buildings[cols]

        # TODO: save buildings in disk
        # buildings.to_parquet()

        bld_count = buildings[["zone_id", "ovm_id"]].groupby("zone_id").count()
        bld_area = buildings[["zone_id", "area"]].groupby("zone_id").sum()

        with self.project.db_connection as conn:
            conn.execute("ALTER TABLE zones ADD ovm_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD ovm_bld_area FLOAT;")

            for zone_id, row in bld_count.iterrows():
                count_qry = "UPDATE zones SET ovm_bld_count={} WHERE zone_id={}".format(row["ovm_id"], zone_id)
                conn.execute(count_qry)

            for zone_id, row in bld_area.iterrows():
                area_qry = "UPDATE zones SET ovm_bld_area={} WHERE zone_id={}".format(row["area"], zone_id)
                conn.execute(area_qry)

            conn.execute("UPDATE zones SET ovm_bld_area=0, ovm_bld_count=0 WHERE ovm_bld_area IS NULL;")

    def import_places(self):
        pass
