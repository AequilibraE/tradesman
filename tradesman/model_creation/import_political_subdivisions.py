import sqlite3
from tempfile import gettempdir
import warnings
from fiona import listlayers
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
import requests
from aequilibrae.project import Project
from os.path import join, isfile
from shapely.geometry import Polygon, MultiPolygon
import pycountry
import urllib
from numpy import arange


class ImportPoliticalSubdivisions:
    def __init__(self, model_place: str, project: Project):

        self.__model_place = model_place
        self.__search_place = model_place.lower().replace(" ", "+")
        self._project = project
        conn = sqlite3.connect(join("project_database.sqlite"))
        self.__all_tables = [
            x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()
        ]

        self.__initialize()
        self._save_model_boundaries()

    def add_country_borders(self, source: str, overwrite: bool):
        self.__source_control(source)

        if source == "gadm":
            data = self._gadm_search()
        else:
            data = self._geoboundaries_search()

        data = data[data.level == 0]

        if overwrite or "political_subdivisions" not in self.__all_tables:
            self._project.conn.execute("DELETE FROM political_subdivisions WHERE level=0;")
            self._project.conn.commit()

            sql = """INSERT INTO political_subdivisions(country_name, division_name, level, geometry)
                        VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"""
            self._project.conn.executemany(sql, list(data.itertuples(index=False, name=None)))
            self._project.conn.commit()

    def import_subdivisions(self, source: str, level: int, overwrite: bool):
        self.__source_control(source)

        data = self.__get_subdivisions(source)[["country_name", "division_name", "level", "geom"]]
        data = data[data.level > 0]

        level = max(data.level) if level > max(data.level) else min(data.level) + level
        data = data[data.level <= level]
        data.sort_values(by="level", ascending=True, inplace=True)

        if overwrite or "political_subdivisions" not in self.__all_tables:
            self._project.conn.execute("DELETE FROM political_subdivisions WHERE level>0;")
            self._project.conn.commit()

            qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
                VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
            list_of_tuples = list(data.itertuples(index=False, name=None))

            self._project.conn.executemany(qry, list_of_tuples)
            self._project.conn.commit()

    def _gadm_search(self):
        gadm_url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{self._country_code}.gpkg"

        dest_path = join(gettempdir(), f"gadm_{self._country_code}.gpkg")

        if not isfile(dest_path):
            urllib.request.urlretrieve(gadm_url, dest_path)

        layers = listlayers(dest_path)
        layers.reverse()

        levels_to_add = []
        counter = len(layers[:-1])

        for i in layers:
            if i != "ADM_ADM_0":
                df = gpd.read_file(dest_path, layer=i)
                df.reset_index(inplace=True)
                centroids = df.to_crs(3857).centroid.to_crs(4326)
                df = df.iloc[centroids[centroids.within(self._poly)].index]
                df = df.assign(level=counter)
                df.rename(columns={"COUNTRY": "country_name", f"NAME_{counter}": "division_name"}, inplace=True)
                levels_to_add.append(df[["country_name", "division_name", "level", "geometry"]])

                counter -= 1
            else:
                df = gpd.read_file(dest_path, layer="ADM_ADM_0")
                df = df.assign(level=0, division_name="country_border")
                df.rename(columns={"COUNTRY": "country_name"}, inplace=True)
                levels_to_add.append(df[["country_name", "division_name", "level", "geometry"]])

        df = pd.concat(levels_to_add)

        df["geom"] = gpd.GeoSeries.to_wkb(df.geometry)

        df.to_parquet(join(gettempdir(), f"{self._country_code.lower()}_cache_gadm.parquet"))

        return df[["country_name", "division_name", "level", "geom"]]

    def _geoboundaries_search(self):

        counter = 5
        link_list = []
        level_list = []
        all_data = []

        while counter >= 0:
            url = f"https://www.geoboundaries.org/gbRequest.html?ISO={self._country_code}&ADM=ADM{counter}"
            r = requests.get(url)
            if len(r.json()) > 0:
                link_list.append(r.json()[0]["gjDownloadURL"])
                level_list.append(counter)
            counter -= 1

        level_list.reverse()
        link_list.reverse()

        for lev in level_list:

            geoBoundary = requests.get(link_list[lev]).json()

            adm_level = {}
            for boundary in geoBoundary["features"]:

                adm_name = boundary["properties"]["shapeName"]

                if adm_name not in adm_level:
                    adm_level[adm_name] = []

                adm_level[adm_name].append(self.__geometry_type(boundary["geometry"]))

            for key, value in adm_level.items():
                adm_level[key] = unary_union(value).wkb

            df = pd.DataFrame.from_dict(adm_level, orient="index", columns=["geom"])
            df.reset_index(inplace=True)
            df.rename(columns={"index": "division_name"}, inplace=True)
            df = df.assign(country_name=self._country_name, level=lev)

            gs = gpd.GeoSeries.from_wkb(df.geom)
            gdf = gpd.GeoDataFrame(df, geometry=gs, crs=4326)
            if lev > 0:
                centroids = gdf.to_crs(3857).centroid.to_crs(4326)
                gdf = gdf.iloc[centroids[centroids.within(self._poly)].index]

            all_data.append(gdf)

        if len(all_data):
            all_data = pd.concat(all_data)
            all_data["idx"] = arange(len(all_data))
            all_data.set_index("idx", inplace=True)
            all_data.at[0, "division_name"] = "country_border"

        all_data.to_parquet(join(gettempdir(), f"{self._country_code.lower()}_cache_geoboundaries.parquet"))

        return all_data[["country_name", "division_name", "level", "geom"]]

    def __geometry_type(self, dct):

        if dct["type"] == "Polygon":
            return Polygon([(coordinate[0], coordinate[1]) for coordinate in dct["coordinates"][0]])
        elif dct["type"] == "MultiPolygon":
            poly = [
                [(coordinate[0], coordinate[1]) for coordinate in dct["coordinates"][i][0]]
                for i in range(len(dct["coordinates"]))
            ]
            return MultiPolygon([Polygon(i) for i in poly])

    def __initialize(self):

        nom_url = f"https://nominatim.openstreetmap.org/search?q={self.__search_place}&format=json&polygon_geojson=1&addressdetails=1&accept-language=en"

        r = requests.get(nom_url)

        if len(r.json()) == 0:
            raise ValueError("The desired model place is not available.")

        self._poly = self.__geometry_type(r.json()[0]["geojson"])

        self._country_code = pycountry.countries.search_fuzzy(r.json()[0]["address"]["country"])[0].alpha_3
        self._country_name = pycountry.countries.search_fuzzy(r.json()[0]["address"]["country"])[0].name

    def __source_control(self, source):
        if source not in ["gadm", "geoboundaries"]:
            raise ValueError("Source not available")

    def __get_subdivisions(self, source):
        if source == "gadm":
            if not isfile(join(gettempdir(), f"{self._country_code.lower()}_cache_gadm.parquet")):
                raise ValueError("Data Source from country_borders is different from political_subdivisions.")
            return gpd.read_parquet(join(gettempdir(), f"{self._country_code.lower()}_cache_gadm.parquet"))
        elif source == "geoboundaries":
            if not isfile(join(gettempdir(), f"{self._country_code.lower()}_cache_geoboundaries.parquet")):
                raise ValueError("Data Source from country_borders is different from political_subdivisions.")
            return gpd.read_parquet(join(gettempdir(), f"{self._country_code.lower()}_cache_geoboundaries.parquet"))

    def _save_model_boundaries(self):
        df = (
            pd.DataFrame([self._poly.wkt], columns=["geometry"])
            if type(self._poly) == Polygon
            else pd.DataFrame([unary_union(list(self._poly.geoms)).wkt], columns=["geometry"])
        )

        gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df.geometry), crs=4326)
        gdf = gdf.assign(level=-1, division_name="model_area", country_name=f"{self._country_name}")
        gdf["geom"] = gdf.geometry.to_wkb()

        qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
                VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
        list_of_tuples = list(
            gdf[["country_name", "division_name", "level", "geom"]].itertuples(index=False, name=None)
        )

        self._project.conn.executemany(qry, list_of_tuples)
        self._project.conn.commit()
        # return gdf

    @property
    def country_name(self):
        return self._country_name

    @property
    def model_place(self):
        return self.__model_place
