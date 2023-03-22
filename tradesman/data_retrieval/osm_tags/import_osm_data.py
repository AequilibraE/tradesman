import geopandas as gpd
import numpy as np
import pandas as pd
from aequilibrae.project import Project
from shapely.geometry import Point, Polygon, box

from tradesman.data.load_zones import load_zones
from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag
from tradesman.data_retrieval.osm_tags.osm_tag_values import amenity_values, building_values


class ImportOsmData:
    """
    Triggers the import of OSM data and saves it into the database.

    Parameters:
         *tag*(:obj:`str`): data tag to download
         *project*(:obj:`aequilibrae.project`): currently open project
         *osm_data*(:obj:`dict`): dictionary to store downloaded data

    """

    def __init__(self, tag: str, project: Project, osm_data: dict):
        self.__tag = tag
        self._project = project
        self.__zones = load_zones(project)
        self.__osm_data = osm_data
        self.__columns = {
            "amenity": ["type", "id", "amenity", "zone_id", "geom"],
            "building": ["type", "id", "building", "zone_id", "area", "geom"],
        }
        self.__query_fields = {
            "amenity": {
                "tag_value": "amenity",
                "field_name": "",
                "field_value": "",
                "geom_type": "Point",
                "field_type": "",
            },
            "building": {
                "tag_value": "building",
                "field_name": "area, ",
                "field_value": "ROUND(?, 2), ",
                "geom_type": "MultiPolygon",
                "field_type": ', "area" FLOAT',
            },
        }
        self.__all_tables = [
            x[0] for x in project.conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()
        ]

        self.__initialize()

    def import_osm_data(self):
        """
        Imports OSM data.

        Parameters:
            *tile_size*(:obj:`int`): tile size (in kilometers)
        """
        df = pd.DataFrame.from_dict(generic_tag(self.__tag, self.__osm_data, self._project))

        if len(df) == 0:
            return

        tag_value = building_values if self.__tag == "building" else amenity_values

        df["geom"] = df.apply(self.__point_or_polygon, axis=1)

        df["tags"] = df["tags"].apply(pd.Series)[self.__tag].values

        df["update_tags"] = df["tags"].apply(lambda x: tag_value.get(x))

        df.update_tags.fillna("undetermined", inplace=True)

        df.drop(columns=["tags"], inplace=True)

        df.rename(columns={"update_tags": self.__tag}, inplace=True)

        clean_df = df[["type", "id", "geom", self.__tag]]

        gdf = gpd.GeoDataFrame(clean_df, geometry=gpd.GeoSeries.from_wkb(clean_df.geom), crs=4326)

        tag_by_zone = gpd.sjoin(gdf, self.__zones)

        tag_by_zone.drop(columns="index_right", inplace=True)

        # Save count and area information within the project's zones database
        counting_table = tag_by_zone.groupby("zone_id").count()[[self.__tag]].fillna(0)
        counting_table["zone_id"] = [i for i in counting_table.index]

        exp = f"ALTER TABLE zones ADD osm_{self.__tag}_count INT;"
        self._project.conn.execute(exp)
        self._project.conn.commit()

        # For small geographical regions, some zones can have zero buildings and/or amenities
        # So we execute the following query to replace NaN values in zones table by zeros
        zero_counts = [i for i in np.arange(1, len(self.__zones) + 1) if i not in counting_table.zone_id.values]
        count_qry = f"UPDATE zones SET osm_{self.__tag}_count=0 WHERE zone_id=?;"
        self._project.conn.executemany(count_qry, list((x,) for x in zero_counts))
        self._project.conn.commit()

        count_qry = f"UPDATE zones SET osm_{self.__tag}_count=? WHERE zone_id=?;"
        self._project.conn.executemany(count_qry, list(counting_table.itertuples(index=False, name=None)))
        self._project.conn.commit()

        if self.__tag == "building":
            tag_by_zone["area"] = tag_by_zone.to_crs(3857).area

            area_table = tag_by_zone.groupby("zone_id").sum(numeric_only=True)[["area"]].fillna(0)
            area_table["zone_id"] = [i for i in area_table.index]

            self._project.conn.execute("ALTER TABLE zones ADD osm_building_area FLOAT;")
            self._project.conn.commit()

            zero_area = [i for i in np.arange(1, len(self.__zones) + 1) if i not in area_table.zone_id.values]
            # area_qry = area_query(area_table, func="set_zero")
            area_qry = "UPDATE zones SET osm_building_area=0 WHERE zone_id=?"
            self._project.conn.executemany(area_qry, list((x,) for x in zero_area))
            self._project.conn.commit()

            # area_qry = area_query(area_table)
            area_qry = "UPDATE zones SET osm_building_area=ROUND(?,2) WHERE zone_id=?;"
            self._project.conn.executemany(area_qry, list(area_table.itertuples(index=False, name=None)))
            self._project.conn.commit()

        # Create a database to store the data
        key = self.__query_fields[self.__tag]

        if f"osm_{self.__tag}" not in self.__all_tables:
            self._project.conn.execute(
                f'CREATE TABLE IF NOT EXISTS osm_{key["tag_value"]}("type" TEXT, "id" INTEGER, "{key["tag_value"]}" TEXT, "zone_id" INTEGER{key["field_type"]});'
            )
            self._project.conn.execute(
                f"SELECT AddGeometryColumn('osm_{key['tag_value']}', 'geometry', 4326, '{key['geom_type'].upper()}', 'XY' );"
            )
            self._project.conn.execute(f"SELECT CreateSpatialIndex('osm_{key['tag_value']}', 'geometry' );")
            self._project.conn.commit()

        qry = f"INSERT INTO osm_{key['tag_value']}(type, id, {key['tag_value']}, zone_id, {key['field_name']}geometry) VALUES(?, ?, ?, ?, {key['field_value']}CastTo{key['geom_type']}(ST_GeomFromWKB(?, 4326)));"

        list_of_tuples = list(tag_by_zone[self.__columns[self.__tag]].fillna(0).itertuples(index=False, name=None))

        self._project.conn.executemany(qry, list_of_tuples)
        self._project.conn.commit()

        return tag_by_zone

    def __initialize(self):
        """
        Checks the desired tag. Currently supports only amenity and building.
        """
        if self.__tag not in ["amenity", "building"]:
            raise ValueError("Tag value not available.")

    @property
    def tag_value(self):
        """Return the tag value."""
        return self.__tag

    def __point_or_polygon(self, row):
        """
        Write the WKB of a Point or a Polygon.

        Parameters:
            *row*(:obj:`pd.DataFrame`): rows of a pandas' DataFrame.
        """
        if row.type != "node" and len(row.geometry) < 4:
            return box(*row.bounds.values()).wkb
        elif row.type != "node" and len(row.geometry) >= 4:
            return Polygon([(dct["lon"], dct["lat"]) for dct in row.geometry]).wkb
        else:
            return Point(np.array([row.lon, row.lat])).wkb
