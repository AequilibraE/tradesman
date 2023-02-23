from os.path import isfile, join
import re
from tempfile import gettempdir

import geopandas as gpd
import pandas as pd
import pycountry
import requests
from aequilibrae.project import Project
from numpy import arange
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


class ImportPoliticalSubdivisions:
    """
    Imports all political subdivisions into the model.

    Parameters:
        *model_place*(:obj:`str`): current model place
        *source*(:obj:`str`): database source to download geographic data. Defaults to GADM
        *project*(:obj:`aequilibrae.project`): currently open project
    """

    def __init__(self, model_place: str, source: str, project: Project):
        self.__model_place = model_place
        self.__search_place = model_place.lower().replace(" ", "+")
        self._project = project
        self._source = source.lower()

        self.__source_control()

    def add_country_borders(self, overwrite: bool = False):
        """
        Add the model's country border.

        Parameters:
             *overwrite*(:obj:`bool`): re-write country borders if it already exists. Defaults to False.
        """
        data = self.__get_subdivisions()[["country_name", "division_name", "level", "geom"]]

        data = data[data.level == 0]

        if overwrite:
            self._project.conn.execute("DELETE FROM political_subdivisions WHERE level=0;")
            self._project.conn.commit()

        sql = """INSERT INTO political_subdivisions(country_name, division_name, level, geometry)
                    VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"""
        self._project.conn.executemany(sql, list(data.itertuples(index=False, name=None)))

        # If the model area is a country, we update the model area to avoid creating useless zones in the future
        if re.search(self.__model_place, self._project.about.country_name):
            sql = """UPDATE political_subdivisions SET geometry=CastToMulti(GeomFromWKB(?, 4326)) WHERE level=-1;"""
            self._project.conn.execute(sql, data.geom.values)

        self._project.conn.commit()

    def import_subdivisions(self, level: int, overwrite: bool = False):
        """
        Add the model's subdivisions. If the model area is smaller than the smallest geographical subdivision from
        GADM or geoBoundaries, it adds the upper-level geometries to the model file.  Otherwise, it adds the
        lower-level geometries which intersect model area.

        Parameters:
             *level*(:obj:`int`): number of levels to download.
             *overwrite*(:obj:`bool`): overwrite political subdivisions if it already exists. Defaults to False.
        """
        data = self.__get_subdivisions()

        if len(data) == 1:
            return

        divisions = data[data.level > 0]

        centers = self.__get_centroids(divisions)
        data = divisions[divisions.index.isin(centers[centers.within(self._poly)].index + 1)]
        if len(data) == 0:
            pos = divisions.sindex.query(geometry=self._poly, predicate="intersects")
            data = divisions.iloc[pos]

        data = data[["country_name", "division_name", "level", "geom"]]
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

    def __boundaries_import(self):
        """
        Imports political boundaries for an entire country. Data for all levels is stored in a parquet file.
        """
        country_data = []

        if self._source == "gadm":
            url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{}_{}.json"
        else:
            url = "https://www.geoboundaries.org/data/geoBoundaries-3_0_0/{}/ADM{}/geoBoundaries-3_0_0-{}-ADM{}.geojson"

        for level in range(5):  # because we have at most 4 subdivision levels
            fmt = (
                url.format(self._project.about.country_code, level)
                if self._source == "gadm"
                else url.format(self._project.about.country_code, level, self._project.about.country_code, level)
            )
            req = requests.get(fmt)
            if req.status_code == 404:
                continue
            req = req.json()

            adm_level = {}
            places = {}
            for boundary in req["features"]:
                if level == 0:
                    adm_name = (
                        boundary["properties"]["COUNTRY"]
                        if self._source == "gadm"
                        else boundary["properties"]["shapeName"]
                    )
                else:
                    adm_name = (
                        boundary["properties"][f"NAME_{level}"]
                        if self._source == "gadm"
                        else boundary["properties"]["shapeName"]
                    )

                if adm_name not in adm_level:
                    adm_level[adm_name] = []

                adm_level[adm_name].append(self.__geometry_type(boundary["geometry"]))

            for key, value in adm_level.items():
                for idx, val in enumerate(value):
                    places[f"{key}_{idx}"] = val.wkb

            df = pd.DataFrame.from_dict(places, orient="index", columns=["geom"])
            df.reset_index(inplace=True)
            df.rename(columns={"index": "division_name"}, inplace=True)
            df = df.assign(country_name=self._project.about.country_name, level=level)

            gs = gpd.GeoSeries.from_wkb(df.geom)
            country_data.append(gpd.GeoDataFrame(df, geometry=gs, crs=4326))

        if len(country_data):
            country_data = pd.concat(country_data)
            country_data["idx"] = arange(len(country_data))
            country_data.set_index("idx", inplace=True)
            country_data.at[0, "division_name"] = "country_border"
            country_data = country_data.drop_duplicates(subset=["division_name", "level"])

        country_data.to_parquet(join(gettempdir(), f"{self._project.about.country_name}_cache_{self._source}.parquet"))

        return country_data[["country_name", "division_name", "level", "geom"]]

    def __geometry_type(self, dct):
        """
        Returns shapely.Polygons or shapely.MultiPolygons.

        Parameters:
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

    def __source_control(self):
        """Checks if the political subdivision source exists."""
        if self._source not in ["gadm", "geoboundaries"]:
            raise ValueError("Source not available.")

    def __get_subdivisions(self):
        """
        Returns the parquet file with political subdivisions.
        """
        file_name = join(gettempdir(), f"{self._project.about.country_name}_cache_{self._source}.parquet")
        if isfile(file_name):
            return gpd.read_parquet(file_name)
        else:
            return self.__boundaries_import()

    @property
    def model_place(self):
        """Returns the name of the place for which the model was build."""
        return self.__model_place

    def __add_model_place_info_to_db(self):
        """
        Adds model place information into the project database.
        """
        about = self._project.about
        about.add_info_field("country_name")
        about.add_info_field("country_code")

        about.model_name = self.__model_place
        about.country_name = self._country_name
        about.country_code = self._country_code

        about.write_back()

    def __get_centroids(self, df):
        """
        Returns a GeoSeries with geometries centroids.
        For geometries that are MultiPolygons, we consider the centroid of the largest shape.

        Parameters:
            *df*(:obj:`geopandas.GeoDataFrame`): geopandas.GeoDataFrame
        """
        centers = []
        for _, row in df.iterrows():
            place = row.geometry
            if type(place) == MultiPolygon:
                if len(place.geoms) == 1:
                    centers.append(place.centroid)
                else:
                    areas = []
                    for p in place.geoms:
                        areas.append(p.area)
                    centers.append(place.geoms[areas.index(max(areas))].centroid)
            else:
                centers.append(place.centroid)

        return gpd.GeoSeries(centers)
