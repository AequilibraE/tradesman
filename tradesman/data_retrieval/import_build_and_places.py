import logging
from os import mkdir
from os.path import dirname, isdir, join
from uuid import uuid4
from tempfile import gettempdir

import duckdb
import geopandas as gpd
import pandas as pd
from aequilibrae.project import Project

overture_url = "s3://overturemaps-us-west-2/release/2025-09-24.0"


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

    def import_data(self, theme: str = "buildings"):
        conn = duckdb.connect()
        c = conn.cursor()

        c.execute("""INSTALL spatial; INSTALL httpfs; INSTALL parquet;""")
        c.execute("""LOAD spatial; LOAD parquet; SET s3_region='us-west-2';""")

        if not isdir(self.project.project_base_path / "ovm_data"):
            mkdir(self.project.project_base_path / "ovm_data")

        logging.info(f"Downloading {theme} from Overture maps. Sit tight! This may take a while.")
        tmp_name = f"{gettempdir()}/{uuid4()}.parquet"

        qrys = {
            "buildings": f"""COPY (
                            SELECT
                                id as ovm_id,
                                sources[1].dataset as source_dataset,
                                sources[1].record_id as source_id,
                                subtype,
                                class,
                                geometry
                            FROM
                                read_parquet('{overture_url}/theme=buildings/type=building/*', filename=true, hive_partitioning=1, union_by_name = true)
                            WHERE
                                bbox.ymin >= {self.__ymin} AND
                                bbox.xmin >= {self.__xmin} AND
                                bbox.ymax <= {self.__ymax} AND
                                bbox.xmax <= {self.__xmax}
                            ) TO '{tmp_name}' WITH (FORMAT 'parquet', COMPRESSION 'ZSTD');""",
            "places": f"""COPY (
                        SELECT
                            id as ovm_id,
                            sources[1].dataset as source_dataset,
                            sources[1].record_id as source_id,
                            categories.primary as tags,
                            categories.alternate as secondary_tags,
                            geometry
                        FROM
                            read_parquet('{overture_url}/theme=places/type=place/*')
                        WHERE
                            bbox.ymin >= {self.__ymin} AND
                            bbox.xmin >= {self.__xmin} AND
                            bbox.ymax <= {self.__ymax} AND
                            bbox.xmax <= {self.__xmax}
                        ) TO '{tmp_name}' WITH (FORMAT 'parquet', COMPRESSION 'ZSTD');""",
        }
        _ = c.execute(qrys[theme])

        logging.info(f"{theme} data downloaded. Basic geo-processing")
        df = pd.read_parquet(tmp_name)

        gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkb(df.geometry, crs=4326))
        gdf = gpd.sjoin(gdf, self.zones)  # Join with the zones database
        gdf = gdf.drop_duplicates(["ovm_id"]).reset_index(drop=True)

        if theme == "buildings":
            gdf["subtype"] = gdf["subtype"].fillna("undetermined")
            gdf["class"] = gdf["class"].fillna("undetermined")
            gdf["area"] = gdf.geometry.to_crs(3857).area

            gdf = gdf[["ovm_id", "source_id", "source_dataset", "subtype", "class", "zone_id", "area", "geometry"]]

            area = gdf[["zone_id", "area"]].groupby("zone_id").sum()
            with self.project.db_connection as conn:
                conn.execute("ALTER TABLE zones ADD ovm_bld_area FLOAT;")
                if not area.empty:
                    for zone_id, row in area.iterrows():
                        area_qry = "UPDATE zones SET ovm_bld_area={} WHERE zone_id={}".format(row["area"], zone_id)
                        conn.execute(area_qry)

                conn.execute("UPDATE zones SET ovm_bld_area=0 WHERE ovm_bld_area IS NULL;")

        elif theme == "places":
            categories = pd.read_csv(join(dirname(__file__), "ovm_tags/ovm_categories.csv"), sep=",")

            gdf = gdf.merge(categories, on="tags")
            gdf = gdf[
                [
                    "ovm_id",
                    "source_id",
                    "source_dataset",
                    "main_category",
                    "tags",
                    "secondary_tags",
                    "zone_id",
                    "geometry",
                ]
            ]

        gdf.to_parquet(self.project.project_base_path / "ovm_data" / f"ovm_{theme}.parquet")

        counts = gdf[["ovm_id", "zone_id"]].groupby("zone_id").count()

        with self.project.db_connection as conn:
            tag = "poi" if theme == "places" else "bld"
            conn.execute(f"ALTER TABLE zones ADD ovm_{tag}_count INT;")

            if not counts.empty:
                for zone_id, row in counts.iterrows():
                    count_qry = f"UPDATE zones SET ovm_{tag}_count={row['ovm_id']} WHERE zone_id={zone_id}"
                    conn.execute(count_qry)

            conn.execute(f"UPDATE zones SET ovm_{tag}_count=0 WHERE ovm_{tag}_count IS NULL;")
