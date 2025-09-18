import gzip
import math
import warnings
from io import StringIO
from os import mkdir
from os.path import isdir, isfile, join
from tempfile import gettempdir
from typing import Tuple, Set
from urllib.request import urlretrieve

import geopandas as gpd
import pandas as pd
import requests
from aequilibrae.project import Project
from aequilibrae.project.network.osm.osm_params import http_headers
from shapely import box


class ImportMicrosoftBuildingData:
    """
    Triggers the import of building information from Microsoft Bing.

    Parameters:
        **project**(:obj:`aequilibrae.project`): currently open project
    """

    def __init__(self, project: Project):
        self.project = project
        self.about = self.project.about

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

    def get_quadkeys_in_bbox(self, xmin: float, ymin: float, xmax: float, ymax: float, zoom: int = 9) -> Set[str]:
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
        except requests.exceptions.Timeout as e:
            raise TimeoutError("Request timed out") from e
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        quadkeys = self.get_quadkeys_in_bbox(
            float(self.about.xmin), float(self.about.ymin), float(self.about.xmax), float(self.about.ymax)
        )
        quadkeys = [int(x) for x in quadkeys]

        # Check if the quadkeys where the model area is has any data to be downloaded.
        # We also check if the quadkey location matches the country_name to avoid downloading
        # unnecessary data (one quadkey can represent more than one country).
        bld_list = bld_list[bld_list["quadkey"].isin(quadkeys)]
        bld_list = bld_list[bld_list["location"] == self.project.about.country_name]
        if bld_list.empty:
            warnings.warn("There is no building footage available for the desired model area.")
            return

        frame_list = []

        for _, row in bld_list.iterrows():
            file_name = f"mcr--building--footage--{self.about.country_name.lower()}--quadkey--{row['quadkey']}.gz"
            dest_path = join(gettempdir(), file_name)
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
        buildings.reset_index(drop=True, inplace=True)
        buildings["id"] = buildings.index + 1
        buildings["area"] = buildings.geometry.to_crs(3857).area

        cols = ["id", "quadkey", "zone_id", "area", "geometry"]
        buildings = buildings[cols]

        if not isdir(self.project.project_base_path / "data_download"):
            mkdir(self.project.project_base_path / "data_download")
        buildings.to_parquet(self.project.project_base_path / "data_download" / "mcr_buildings.parquet")

        bld_count = buildings[["zone_id", "id"]].groupby("zone_id").count()
        bld_area = buildings[["zone_id", "area"]].groupby("zone_id").sum()

        with self.project.db_connection as conn:
            # Create columns in zones' table with microsoft building information
            conn.execute("ALTER TABLE zones ADD mcr_bld_count INT;")
            conn.execute("ALTER TABLE zones ADD mcr_bld_area FLOAT;")

            if not bld_count.empty:
                for zone_id, row in bld_count.iterrows():
                    count_qry = "UPDATE zones SET mcr_bld_count={} WHERE zone_id={}".format(row["id"], zone_id)
                    conn.execute(count_qry)

            if not bld_area.empty:
                for zone_id, row in bld_area.iterrows():
                    area_qry = "UPDATE zones SET mcr_bld_area={} WHERE zone_id={}".format(row["area"], zone_id)
                    conn.execute(area_qry)

            conn.execute("UPDATE zones SET mcr_bld_area=0, mcr_bld_count=0 WHERE mcr_bld_area IS NULL;")
