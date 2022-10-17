import gzip
from os.path import isfile, join
from tempfile import gettempdir
from urllib.request import urlretrieve

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from aequilibrae.project import Project

from tradesman.data.load_zones import load_zones


class ImportMicrosoftBuildingData:
    def __init__(self, model_place: str, project: Project):
        self.__model_place = model_place
        self._project = project
        self.__zones = load_zones(project)
        self.__country_list = pd.read_csv(
            "https://raw.githubusercontent.com/microsoft/GlobalMLBuildingFootprints/main/dataset-links.csv"
        )

        self.__country_name = self.__nominatim_get_name()

        self.__initialize()

    def __nominatim_get_name(self):
        nom_url = f"https://nominatim.openstreetmap.org/search?q={self.__model_place}&format=json&polygon_geojson=1&addressdetails=1&accept-language=en"

        r = requests.get(nom_url)

        return r.json()[0]["address"]["country"]

    def __initialize(self):
        if self.__country_name not in self.__country_list.Location.values:
            raise FileNotFoundError("Microsoft Bing does not provide information about this region.")

    def microsoft_buildings(self):

        url = self.__country_list[self.__country_list.Location == self.__country_name].Url.values

        frame_list = []

        for i in range(len(url)):
            dest_path = join(gettempdir(), f"{self.__country_name}_{i}_bing.gz")

            if not isfile(dest_path):
                urlretrieve(url[i], dest_path)

            with gzip.open(dest_path, "rb") as file:
                frame_list.append(gpd.read_file(file))

        model_gdf = pd.concat(frame_list)

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

        qry = "UPDATE zones SET microsoft_building_count=?, microsoft_building_area=ROUND(?, 2) WHERE zone_id=?;"
        list_of_tuples = list(
            zip(
                buildings_by_zone.groupby("zone_id").count().id.values,
                buildings_by_zone.groupby("zone_id").sum().area.values,
                np.arange(1, max(buildings_by_zone.zone_id) + 1),
            )
        )
        self._project.conn.executemany(qry, list_of_tuples)
        self._project.conn.commit()
