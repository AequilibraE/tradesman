from os.path import isfile, join
from tempfile import gettempdir
from urllib.request import urlretrieve

import geopandas as gpd
import pandas as pd
import pycountry
import requests
from aequilibrae.project import Project
from fiona import listlayers
from numpy import arange
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


class ImportPoliticalSubdivisions:
    """
    Imports all political subdivisions into the model.
    """

    def __init__(self, model_place: str, source: str, project: Project):

        self.__model_place = model_place
        self.__search_place = model_place.lower().replace(" ", "+")
        self._project = project
        self._source = source.lower()

        self.__source_control(self._source)

    def add_country_borders(self, overwrite: bool):
        """
        Add the model's country border.

        Args.:
             *overwrite*(:obj:`bool`): re-write country borders if it already exists. Defaults to False.
        """
        data = self._gadm_search() if self._source == "gadm" else self._geoboundaries_search()

        data = data[data.level == 0]

        if overwrite:
            self._project.conn.execute("DELETE FROM political_subdivisions WHERE level=0;")
            self._project.conn.commit()

        sql = """INSERT INTO political_subdivisions(country_name, division_name, level, geometry)
                    VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"""
        self._project.conn.executemany(sql, list(data.itertuples(index=False, name=None)))
        self._project.conn.commit()

    def import_subdivisions(self, level: int, overwrite: bool):
        """
        Add the model's subdivisions. If the model area is smaller than the smallest geographical subdivision from GADM or geoBoundaries, it adds the upper-level geometries to the model file. Otherwise, it adds the lower-level geometries which intersect model area.

        Args.:
             *level*(:obj:`int`): number of levels to download.
             *overwrite*(:obj:`bool`): re-write political subdivisions if it already exists. Defaults to False.
        """

        data = self.__get_subdivisions(self._source)[["country_name", "division_name", "level", "geom"]]

        if len(data) == 1:
            return

        data = data[data.level > 0]

        level = max(data.level) if level > max(data.level) else min(data.level) + level
        data = data[data.level <= level]
        data.sort_values(by="level", ascending=True, inplace=True)

        if overwrite:
            self._project.conn.execute("DELETE FROM political_subdivisions WHERE level>0;")
            self._project.conn.commit()

        qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
            VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
        list_of_tuples = list(data.itertuples(index=False, name=None))

        self._project.conn.executemany(qry, list_of_tuples)
        self._project.conn.commit()

    def _gadm_search(self):
        """
        Download political subdivisions from GADM.
        """
        gadm_url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{self._country_code}.gpkg"

        dest_path = join(gettempdir(), f"gadm_{self._country_code}.gpkg")

        if not isfile(dest_path):
            urlretrieve(gadm_url, dest_path)

        layers = listlayers(dest_path)
        layers.reverse()

        levels_to_add = []
        counter = len(layers[:-1])

        for i in layers:
            if i != "ADM_ADM_0":
                df = gpd.read_file(dest_path, layer=i)
                df.reset_index(inplace=True)
                centroids = df.to_crs(3857).centroid.to_crs(4326)
                gdf = df.iloc[centroids[centroids.within(self._poly)].index]
                if len(gdf) == 0:
                    pos = df.sindex.query(geometry=self._poly, predicate="intersects")
                    gdf = df.iloc[pos]
                gdf = gdf.assign(level=counter)
                gdf.rename(columns={"COUNTRY": "country_name", f"NAME_{counter}": "division_name"}, inplace=True)
                levels_to_add.append(gdf[["country_name", "division_name", "level", "geometry"]])

                counter -= 1
            else:
                df = gpd.read_file(dest_path, layer="ADM_ADM_0")
                df = df.assign(level=0, division_name="country_border")
                df.rename(columns={"COUNTRY": "country_name"}, inplace=True)
                levels_to_add.append(df[["country_name", "division_name", "level", "geometry"]])

        df = pd.concat(levels_to_add)

        df["geom"] = gpd.GeoSeries.to_wkb(df.geometry)

        df.to_parquet(join(gettempdir(), f"{self.__model_place}_cache_gadm.parquet"))

        return df[["country_name", "division_name", "level", "geom"]]

    def _geoboundaries_search(self):
        """
        Download political geometries from geoBoundaries
        """
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
                aux = gdf.iloc[centroids[centroids.within(self._poly)].index]
                if len(aux) == 0:
                    pos = gdf.sindex.query(geometry=self._poly, predicate="intersects")
                    gdf = gdf.iloc[pos]
                all_data.append(aux)

            all_data.append(gdf)

        if len(all_data):
            all_data = pd.concat(all_data)
            all_data["idx"] = arange(len(all_data))
            all_data.set_index("idx", inplace=True)
            all_data.at[0, "division_name"] = "country_border"
            all_data = all_data.drop_duplicates(subset=["division_name", "level"])

        all_data.to_parquet(join(gettempdir(), f"{self.__model_place}_cache_geoboundaries.parquet"))

        return all_data[["country_name", "division_name", "level", "geom"]]

    def __geometry_type(self, dct):
        """
        Returns shalepy.Polygons or shapeply.MultiPolygons depending on the data type.

        Args.:
             *dct*(:obj:`dict`): dictionary with coordinates.
        """

        if dct["type"] == "Polygon":
            return Polygon([(coordinate[0], coordinate[1]) for coordinate in dct["coordinates"][0]])
        elif dct["type"] == "MultiPolygon":
            poly = [
                [(coordinate[0], coordinate[1]) for coordinate in dct["coordinates"][i][0]]
                for i in range(len(dct["coordinates"]))
            ]
            return MultiPolygon([Polygon(i) for i in poly])

    def import_model_area(self):
        """
        Add model area into project database.
        """

        if self._project.conn.execute("SELECT COUNT(*) FROM political_subdivisions WHERE level=-1;").fetchone()[0] > 0:
            return

        nom_url = f"https://nominatim.openstreetmap.org/search?q={self.__search_place}&format=json&polygon_geojson=1&addressdetails=1&accept-language=en"

        r = requests.get(nom_url)

        if len(r.json()) == 0:
            raise ValueError("The desired model place is not available.")

        self._poly = self.__geometry_type(r.json()[0]["geojson"])

        self._country_code = pycountry.countries.search_fuzzy(r.json()[0]["address"]["country"])[0].alpha_3
        self._country_name = pycountry.countries.search_fuzzy(r.json()[0]["address"]["country"])[0].name

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

        self.__add_model_place_info_to_db()

    def __source_control(self, source):
        """Checks if the political subdivision source exists."""
        if source not in ["gadm", "geoboundaries"]:
            raise ValueError("Source not available.")

    def __get_subdivisions(self, source):
        """
        Returns the temporary file with poitical subdivisions.

        Args.:
             *source*(:obj:`str`): political subdivision source. Takes GADM or geoBoundaries.
        """
        if source == "gadm":
            return gpd.read_parquet(join(gettempdir(), f"{self.__model_place}_cache_gadm.parquet"))
        else:
            return gpd.read_parquet(join(gettempdir(), f"{self.__model_place}_cache_geoboundaries.parquet"))

    @property
    def model_place(self):
        """Returns the name of the place for which this model was made."""
        return self.__model_place

    def __add_model_place_info_to_db(self):
        about = self._project.about
        about.add_info_field("country_name")
        about.add_info_field("country_code")

        about.model_name = self.__model_place
        about.country_name = self._country_name
        about.country_code = self._country_code

        about.write_back()
