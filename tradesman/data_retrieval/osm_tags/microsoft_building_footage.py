from genericpath import isfile
from tempfile import gettempdir
from urllib.request import urlretrieve
import zipfile
import numpy as np
import pandas as pd
import geopandas as gpd
import pycountry
from os.path import join, dirname
from aequilibrae.project import Project

from tradesman.data.load_zones import load_zones


class ImportMicrosoftBuildingData:
    def __init__(self, model_place: str, project: Project):
        self.__model_place = model_place
        self._project = project
        self.__zones = load_zones(project)
        self.__country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3
        self.__dest_path = join(gettempdir(), f"{self.__country_code}_bing.zip")
        self.__country_list = pd.read_csv(join(dirname(__file__), "data/microsoft_countries_and_territories.csv"))

        self.__initialize()
        self.__downloaded_file()

    def __initialize(self):
        if self.__country_code not in self.__country_list.iso_code.values:
            raise FileNotFoundError("Microsoft Bing does not provide information about this region.")

    def __downloaded_file(self):
        url = self.__country_list[self.__country_list.iso_code == self.__country_code].url.values[0]

        if not isfile(self.__dest_path):
            urlretrieve(url, self.__dest_path)

        zf = zipfile.ZipFile(self.__dest_path)

        zf.extractall(gettempdir())

    def microsoft_buildings(self):
        model_gdf = gpd.read_file(join(gettempdir(), f"{self.__model_place}.geojsonl"))

        model_gdf["area"] = model_gdf.to_crs(3857).geometry.area

        buildings_by_zone = gpd.sjoin(model_gdf, self.__zones)

        buildings_by_zone.drop(columns=["index_right"], inplace=True)

        buildings_by_zone.insert(0, column="id", value=np.arange(1, len(buildings_by_zone) + 1))

        buildings_by_zone["geom"] = buildings_by_zone.geometry.to_wkb()

        # Create columns in zones' table with microsoft buiilding information
        self._project.conn.execute("ALTER TABLE zones ADD microsoft_building_count INT;")
        self._project.conn.commit()

        self._project.conn.execute("ALTER TABLE zones ADD microsoft_building_area FLOAT;")
        self._project.conn.commit()

        self._project.conn.execute(
            "UPDATE zones SET microsoft_building_area=ROUND(0,2), microsoft_building_count=0 WHERE microsoft_building_count IS NULL;"
        )
        self._project.conn.commit()

        qry = "UPDATE zones SET microsoft_building_count=?, microsoft_building_area=ROUND(?, 0) WHERE zone_id=?;"
        list_of_tuples = list(
            zip(
                buildings_by_zone.groupby("zone_id").count().id.values,
                buildings_by_zone.groupby("zone_id").sum().area.values,
                np.arange(1, max(buildings_by_zone.zone_id) + 1),
            )
        )
        self._project.conn.executemany(qry, list_of_tuples)
        self._project.conn.commit()
