import geopandas as gpd
import gzip
import math
import numpy as np
import pandas as pd
import requests
import warnings
from aequilibrae.project import Project
from aequilibrae.project.network.osm.osm_params import http_headers
from io import StringIO
from os.path import isfile, join
from shapely import box
from tempfile import gettempdir
from typing import Tuple, Set
from urllib.request import urlretrieve


class ImportMicrosoftBuildingData:
    """
    Triggers the import of building information from Microsoft Bing.

    Parameters:
        **project**(:obj:`aequilibrae.project`): currently open project
    """

    def __init__(self, project: Project):
        self._project = project

    def lat_lon_to_tile(self, lat: float, lon: float, zoom: int = 9) -> Tuple[int, int]:
        """Convert lat/lon to tile coordinates."""
        lat_rad = math.radians(lat)
        n = 2.0**zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y

    def tile_to_lat_lon(self, x: int, y: int, zoom: int = 9) -> Tuple[float, float, float, float]:
        """Convert tile to bounding box (west, south, east, north)."""
        n = 2.0**zoom
        west = x / n * 360.0 - 180.0
        east = (x + 1) / n * 360.0 - 180.0
        north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
        return west, south, east, north

    def tile_to_quadkey(self, x: int, y: int, zoom: int = 9) -> str:
        """Convert tile coordinates to quadkey."""
        quadkey = ""
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if x & mask:
                digit += 1
            if y & mask:
                digit += 2
            quadkey += str(digit)
        return quadkey

    def get_quadkeys_in_bbox(
        self, xmin: float, ymin: float, xmax: float, ymax: float, zoom: int = 9
    ) -> Set[str]:
        """
        Get all quadkeys that intersect with a bounding box.

        Args:
            xmin, ymin, xmax, ymax: Bounding box coordinates
            zoom: Quadkey zoom level

        Returns:
            Set of quadkey strings
        """
        # Create bounding box
        bbox = box(xmin, ymin, xmax, ymax)

        # Get tile bounds
        min_x, max_y = self.lat_lon_to_tile(ymin, xmin, zoom)
        max_x, min_y = self.lat_lon_to_tile(ymax, xmax, zoom)

        quadkeys = set()

        # Check each tile
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                # Create tile bounding box
                west, south, east, north = self.tile_to_lat_lon(x, y, zoom)
                tile_box = box(west, south, east, north)

                # Check intersection
                if bbox.intersects(tile_box):
                    quadkey = self.tile_to_quadkey(x, y, zoom)
                    quadkeys.add(quadkey)

        return quadkeys

    def get_buildings(self):
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
            # TODO: Gotta raise errors instead
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        bbox = []
        key_list = list(self.get_quadkeys_in_bbox(bbox))

        # Check if the bbox coordinates are within any QuadKey. If the DataFrame is empty, it means that
        # there is no building data for the model area.
        bld_list = bld_list[bld_list["quadkey"].isin(key_list)]
        bld_list = bld_list[bld_list["location"] == self.project.about.country_name]
        if bld_list.empty:
            warnings.warn("There is no building footage available for the desired model area.")
            return

        frame_list = []

        for _, row in bld_list.iterrows():
            dest_path = join(gettempdir(), f"building--footage--quadkey--{row["quadkey"]}.gz")
            if not isfile(dest_path):
                _, _ = urlretrieve(row["url"], dest_path)
            with gzip.open(dest_path, "rb") as file:
                gdf = gpd.read_file(file)
                gdf["quadkey"] = row["quadkey"]
                frame_list.append(gdf)

        zones = self.project.zoning.data.copy()
        zones = zones[["zone_id", "geometry"]]

        buildings = pd.concat(frame_list)
        buildings = gpd.sjoin(buildings, zones)  # Join with the zones database
        buildings["id"] = buildings.index + 1
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["id", "quadkey", "zone_id", "area", "geom"]
        buildings = buildings[cols]

        # TODO: save the data in the disk


        with self._project.db_connection as conn:
            # Create columns in zones' table with microsoft building information
            conn.execute("ALTER TABLE zones ADD mcr_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD mcr_bld_area FLOAT;")

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

