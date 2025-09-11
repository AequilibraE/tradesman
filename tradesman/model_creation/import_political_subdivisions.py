from collections import namedtuple
from os.path import isfile, join
from tempfile import gettempdir

import duckdb
import geopandas as gpd
import pandas as pd
import pycountry
import requests
from aequilibrae.project import Project
from aequilibrae.project.network.osm.osm_params import http_headers
from shapely import wkt
from shapely.geometry import MultiPolygon, Polygon

OVM_MAPPING = {
    "country": 0,
    "dependency": 1,
    "macroregion": 2,
    "region": 3,
    "macrocounty": 4,
    "county": 5,
    "localadmin": 6,
    "locality": 7,
    "borough": 8,
    "macrohood": 9,
    "neighborhood": 10,
    "microhood": 11,
}


class ImportPoliticalSubdivisions:
    """
    Imports all political subdivisions into the model.

    Parameters:
        *model_place*(:obj:`str`): current model place

        *project*(:obj:`aequilibrae.project`): currently open project

        *source*(:obj:`str`): database source to download geographic data. Defaults to Overture
    """

    def __init__(self, model_place: str, project: Project, source: str = "Overture"):
        self.__model_place = model_place
        self.__search_place = model_place.lower().replace(" ", "+")
        self.project = project
        self._source = source.lower()
        self._poly = None

        self.__source_control()

    def add_country_borders(self, overwrite: bool = False):
        """
        Add the model's country border.

        Parameters:
            *overwrite*(:obj:`bool`): re-write country borders if it already exists.
            Defaults to ``False``.
        """
        data = self.__get_subdivisions()
        data = data[data.level == 0].copy()
        data["geom"] = data["geometry"].to_wkb()
        data = data[["country_name", "division_name", "geom"]]

        with self.project.db_connection as conn:
            # If the model area is a country, we update the model area to avoid creating useless zones in the future
            if self.project.about.address_type == "country":
                conn.execute("DELETE FROM political_subdivisions WHERE level=-1;")
                sql = """INSERT INTO political_subdivisions(country_name, division_name, level, geometry)
                         VALUES(?, ?, -1, CastToMulti(GeomFromWKB(?, 4326)));"""
                conn.executemany(sql, list(data.itertuples(False, None)))

            if overwrite:
                conn.execute("DELETE FROM political_subdivisions WHERE level=0;")

            sql = """INSERT INTO political_subdivisions(country_name, division_name, level, geometry)
                     VALUES(?, ?, 0, CastToMulti(GeomFromWKB(?, 4326)));"""
            conn.executemany(sql, list(data.itertuples(index=False, name=None)))

    def import_subdivisions(self, level: int = 2, overwrite: bool = False):
        """
        Add the model's subdivisions. If the model area is smaller than the smallest geographical subdivision from
        overture or geoBoundaries, it adds the upper-level geometries to the model file. Otherwise, it adds the
        lower-level geometries which intersect model area.

        Parameters:
            *level*(:obj:`int`): number of levels to download.
            *overwrite*(:obj:`bool`): overwrite political subdivisions if it already exists. Defaults to False.
        """
        subdiv = self.__get_subdivisions()
        subdiv = subdiv[subdiv.level > 0].copy()

        # There are subdivisions if the geometry centroids are within the model area polygon.
        centroids = self.__get_centroids(subdiv)
        centroids = centroids[centroids.within(self.area_polygon)]
        subdiv = subdiv.iloc[centroids.index]

        # If there are no centroids, then all we have is the modelling area
        if subdiv.shape[0] == 0:
            return

        subdiv["geom"] = subdiv["geometry"].to_wkb()
        subdiv = subdiv[subdiv.level <= subdiv.level.unique()[:level].max()]
        subdiv.sort_values(by=["level", "division_name"], ascending=True, inplace=True)

        subdiv = subdiv[["country_name", "division_name", "level", "geom"]]

        with self.project.db_connection as conn:
            if overwrite:
                conn.execute("DELETE FROM political_subdivisions WHERE level>0;")
                conn.commit()

            qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
                   VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
            list_of_tuples = list(subdiv.itertuples(index=False, name=None))

            conn.executemany(qry, list_of_tuples)

    def __boundaries_import(self):
        """
        Imports political boundaries for an entire country. Data for all levels is stored in a parquet file.
        """
        if self._source == "overture":
            url = "s3://overturemaps-us-west-2/release/2025-07-23.0/theme=divisions/type=division_area/*"
            qry = """
            SELECT
                id as ovm_id,
                division_id,
                subtype,
                names.primary as division_name,
                ST_AsText(geometry) as geometry
            FROM
                read_parquet('{}', hive_partitioning=1)
            WHERE
                country = '{}' AND
                class = 'land'
            """
            qry = qry.format(url, self.project.about.country_code_two_digit)

            # Load duckdb spatial
            conn = duckdb.connect()
            conn.install_extension("spatial")
            conn.load_extension("spatial")

            adm_places = conn.execute(qry).df()
            adm_places = gpd.GeoDataFrame(adm_places, geometry=adm_places["geometry"].apply(wkt.loads), crs="EPSG:4326")
            adm_places["level"] = adm_places["subtype"].map(OVM_MAPPING)
            adm_places["country_name"] = self.project.about.country_name
            adm_places = adm_places.sort_values(by=["level", "division_name"]).reset_index(drop=True)

            cols = ["level", "subtype", "ovm_id", "division_id", "country_name", "division_name", "geometry"]
            adm_places = adm_places[cols]

        else:
            url = "http://www.geoboundaries.org/api/current/gbOpen/{}/ALL/"
            url = url.format(self.project.about.country_code_three_digit)
            Place = namedtuple("Place", ["level", "fid", "geo_id", "country_name", "division_name", "geometry"])

            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"Request failed with status code {response.status_code}")

            adm_places = []
            res = response.json()

            for i, level in enumerate(res):
                lvl_response = requests.get(level["gjDownloadURL"], timeout=self.__timeout, headers=http_headers)
                if lvl_response.status_code != 200:
                    raise ValueError(f"Request failed with status code {response.status_code}")
                inner_res = lvl_response.json()
                for idx, boundary in enumerate(inner_res["features"]):
                    geom = self.__geometry_type(boundary["geometry"])
                    adm_places.extend(
                        [
                            Place(
                                i,
                                idx,
                                boundary["properties"]["shapeID"],
                                self.project.about.country_name,
                                boundary["properties"]["shapeName"],
                                geom.wkb,
                            )
                        ]
                    )

            adm_places = pd.DataFrame(adm_places)
            adm_places = gpd.GeoDataFrame(
                adm_places, geometry=gpd.GeoSeries.from_wkb(adm_places.geometry), crs="EPSG:4326"
            )

        adm_places.to_parquet(join(gettempdir(), f"{self.project.about.country_name}_cache_{self._source}.parquet"))

        return adm_places

    def __geometry_type(self, geometry):
        """
        Returns shapely.Polygons or shapely.MultiPolygons.

        Parameters:
             *geometry*(:obj:`dict`): dictionary with geometry info.
        """

        if geometry["type"] == "Polygon":
            return Polygon(geometry["coordinates"][0])
        elif geometry["type"] == "MultiPolygon":
            max = len(geometry["coordinates"])
            return MultiPolygon([Polygon(geometry["coordinates"][i][0]) for i in range(max)])

    def import_model_area(self):
        """
        Add model area into project database.
        """
        with self.project.db_connection as conn:
            if conn.execute("SELECT COUNT(*) FROM political_subdivisions WHERE level=-1;").fetchone()[0] > 0:
                return

        self.__timeout = 30
        params = {"q": self.__search_place, "format": "json", "polygon_geojson": 1, "addressdetails": 1}

        url = "https://nominatim.openstreetmap.org/"
        url = url.rstrip("/") + "/search"

        try:
            response = requests.get(url, params=params, timeout=self.__timeout, headers=http_headers)
            if response.status_code != 200:
                raise ValueError(f"Request failed with status code {response.status_code}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError("Request timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("Failed to connect") from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error: {e}") from e

        res = response.json()
        if not res:
            raise ValueError("The desired model place is not available.")

        # We add useful place info to the project about table
        country = pycountry.countries.lookup(res[0]["address"]["country"])

        fields = ["model_place", "address_type", "country_name", "country_code_two_digit", "country_code_three_digit"]
        fields.extend(["xmin", "ymin", "xmax", "ymax"])

        about = self.project.about
        for field in fields:
            about.add_info_field(field)

        about.model_place = self.__model_place
        about.address_type = res[0]["addresstype"]
        about.country_name = country.name
        about.country_code_two_digit = country.alpha_2.upper()
        about.country_code_three_digit = country.alpha_3.upper()
        about.xmin = res[0]["boundingbox"][2]
        about.ymin = res[0]["boundingbox"][0]
        about.xmax = res[0]["boundingbox"][3]
        about.ymax = res[0]["boundingbox"][1]

        if "ISO3166-2-lvl4" in res[0]["address"]:
            about.add_info_field("subdivision_code")
            about.subdivision_code = res[0]["address"]["ISO3166-2-lvl4"]

        about.write_back()

        # Manipulate geometry data
        self._poly = self.__geometry_type(res[0]["geojson"])

        df = gpd.GeoDataFrame(
            [[country.name, "model_area", -1]],
            columns=["country_name", "division_name", "level"],
            geometry=[self._poly],
            crs="EPSG:4326",
        )
        df["geom"] = df["geometry"].to_wkb()
        df.drop(["geometry"], axis=1, inplace=True)

        with self.project.db_connection as conn:
            qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
                    VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
            list_of_tuples = list(df.itertuples(False, None))
            conn.executemany(qry, list_of_tuples)

    def __source_control(self):
        """Checks if the political subdivision source exists."""
        if self._source not in ["overture", "geoboundaries"]:
            raise ValueError("Source not available.")

    def __get_subdivisions(self, select_columns: list = None):
        """
        Returns the parquet file with political subdivisions.
        """
        file_name = join(gettempdir(), f"{self.project.about.country_name}_cache_{self._source}.parquet")
        if isfile(file_name):
            if select_columns:
                return gpd.read_parquet(file_name, columns=select_columns)
            else:
                return gpd.read_parquet(file_name)
        else:
            return self.__boundaries_import()

    @property
    def model_place(self):
        """Returns the name of the place for which the model was build."""
        return self.__model_place

    @property
    def area_polygon(self):
        """"""
        with self.project.db_connection as conn:
            qry = "SELECT *, Hex(ST_AsBinary(geometry)) as geom FROM political_subdivisions WHERE level=-1"
            model_area = gpd.GeoDataFrame.from_postgis(qry, conn, geom_col="geom", crs=4326)
            if model_area.empty:
                Warning.warn("No model_area found in project. Please check its import.")
            return model_area.geom[0]

    def __get_centroids(self, gdf):
        """
        Returns a GeoSeries with geometries centroids.
        For geometries that are MultiPolygons, we consider the centroid of the largest shape.

        Parameters:
            *gdf*(:obj:`geopandas.GeoDataFrame`): geopandas.GeoDataFrame
        """
        subset = "ovm_id" if self._source == "overture" else "geo_id"

        x = gdf.explode(index_parts=True).copy()
        x["area"] = x.geometry.to_crs(3845).area
        x = x.sort_values(by=["level", "division_name", "area"]).drop_duplicates(subset=[subset])

        return gpd.GeoDataFrame(
            x[subset], geometry=x["geometry"].to_crs(3845).centroid.to_crs(4326), crs=4326
        ).reset_index(drop=True)
