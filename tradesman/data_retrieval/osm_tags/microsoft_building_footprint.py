import gzip
import warnings
from os.path import isfile, join
from tempfile import gettempdir
from urllib.request import urlretrieve
import math
from io import StringIO

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from aequilibrae.project import Project
from aequilibrae.project.network.osm.osm_params import http_headers

from tradesman.data.load_zones import load_zones


class ImportMicrosoftBuildingData:
    """
    Triggers the import of building information from Microsoft Bing.

    Parameters:
        **project**(:obj:`aequilibrae.project`): currently open project
    """

    def __init__(self, project: Project):
        self._project = project
        self.__zones = load_zones(project)

    def get_quadkey(lat, lng, zoom: int = 9):
        """
        Borrowed from https://medium.com/@biz.soing/generating-quadkeys-83aa2b8018b7
        """
        x = int((lng + 180) / 360 * (1 << zoom))
        y = int(
            (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * (1 << zoom)
        )
        quadkey = ""
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (x & mask) != 0:
                digit += 1
            if (y & mask) != 0:
                digit += 2
            quadkey += str(digit)
        return int(quadkey)

    def microsoft_buildings(self):
        """
        Import building information from Microsoft Bing.
        """
        url = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"

        try:
            # Make request with timeout and headers
            response = requests.get(url, headers=http_headers, timeout=30)
            response.raise_for_status()  # Raise exception for bad status codes

            # Read CSV from response content
            bld_list = pd.read_csv(StringIO(response.text))
            bld_list.columns = [x.lower() for x in bld_list.columns]
        except requests.exceptions.Timeout:
            print("Request timed out after 30 seconds")
            # Gotta raise errors instead
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        bbox = []
        key_list = [
            self.get_quadkey(bbox[0], bbox[2]),
            self.get_quadkey(bbox[1], bbox[2]),
            self.get_quadkey(bbox[0], bbox[3]),
            self.get_quadkey(bbox[1], bbox[3]),
        ]

        # Check if the bbox coordinates are within any QuadKey. If the DataFrame is empty, it means that
        # there is no building data for the model area.
        bld_list = bld_list[bld_list["quadkey"].isin(key_list)]
        if bld_list.empty:
            warnings.warn("There is no building footage available for the desired model area.")
            return

        url = self.__country_list[self.__country_list.Location == self.__country_name].Url.values

        frame_list = []

        for _, row in bld_list.iterrows():
            dest_path = join(gettempdir(), f"building--footage--quadkey--{row["quadkey"]}.gz")
            if not isfile(dest_path):
                _, _ = urlretrieve(row["url"], dest_path)
            with gzip.open(dest_path, "rb") as file:
                gdf = gpd.read_file(file)
                gdf["quadkey"] = row["quadkey"]
                frame_list.append(gdf)

        buildings = pd.concat(frame_list)
        buildings = gpd.sjoin(buildings, self.__zones)  # Join with the zones database
        buildings["id"] = buildings.index + 1
        buildings["geom"] = buildings.geometry.to_wkb()
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["id", "quadkey", "zone_id", "area", "geom"]
        buildings = buildings[cols]

        with self._project.db_connection as conn:
            # Create columns in zones' table with microsoft building information
            conn.execute("ALTER TABLE zones ADD mcr_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD mcr_bld_area FLOAT;")
            conn.commit()

            # Add
            conn.execute(
                """
                    UPDATE zones 
                    SET mcr_bld_area=ROUND(0,2), mcr_bld_count=0 
                    WHERE mcr_bld_count IS NULL;
                """
            )
            conn.commit()

            qry = "UPDATE zones SET mcr_bld_count=?, mcr_bld_area=ROUND(?, 2) WHERE zone_id=?;"
            list_of_tuples = list(
                zip(
                    buildings.groupby("zone_id").count().id.values,
                    buildings.groupby("zone_id").sum(numeric_only=True).area.values,
                    np.arange(1, max(buildings.zone_id) + 1),
                    strict=False,
                )
            )
            conn.executemany(qry, list_of_tuples)
