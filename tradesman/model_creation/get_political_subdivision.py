import json
import requests
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
from shapely import wkb
import pycountry
from aequilibrae import Project
import sqlite3
import warnings
import urllib.request
from os.path import join, isfile
from tempfile import gettempdir
from fiona import listlayers


def get_subdivisions_gadm(model_place: str, lvl: int):
    """
    Import political subdivisions from GADM.
    Parameters:
         *model_place*(:obj:`str`): current model place
         *lvl*(:obj:`int`): number of political subdivisions to add
    """
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{country_code}.gpkg"

    dest_path = join(gettempdir(), f"gadm_{country_code}.gpkg")
    if not isfile(dest_path):
        urllib.request.urlretrieve(url, dest_path)

    if lvl >= len(listlayers(dest_path)):
        return

    levels_to_add = []

    for i in range(1, lvl + 1):
        df = gpd.read_file(dest_path, layer=f"ADM_ADM_{i}")
        df = df[df.COUNTRY == model_place].assign(level=i)
        df.rename(columns={"COUNTRY": "country", f"NAME_{i}": "division_name"}, inplace=True)
        levels_to_add.append(df[["country", "division_name", "level", "geometry"]])

    df = pd.concat(levels_to_add)
    df["geom"] = gpd.GeoSeries.to_wkb(df.geometry)

    return df[["country", "division_name", "level", "geom"]]


def get_subdivisions_online(model_place: str, level: int):
    """
    Import political subdivisions from GeoBoundaries.
    Parameters:
         *model_place*(:obj:`str`): current model place
         *lvl*(:obj:`int`): number of political subdivisions to add
    """
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    all_data = []
    for lev in range(1, level + 1):
        r = requests.get(f"https://www.geoboundaries.org/gbRequest.html?ISO={country_code}&ADM=ADM{lev}")

        if len(r.json()) == 0:
            warnings.warn("The administrative boundary is not available at this level.")
            continue

        dlPath = r.json()[0]["gjDownloadURL"]
        geoBoundary = requests.get(dlPath).json()

        adm_level = {}
        for boundary in geoBoundary["features"]:

            adm_name = boundary["properties"]["shapeName"]
            geo = boundary["geometry"]

            if adm_name not in adm_level:
                adm_level[adm_name] = []

            if boundary["geometry"]["type"] == "MultiPolygon":
                for poly in geo["coordinates"]:
                    adm_level[adm_name].append(Polygon(poly[0]))
            else:
                adm_level[adm_name].append(Polygon(geo["coordinates"][0]))

        for key, value in adm_level.items():
            if len(value) > 1:
                adm_level[key] = unary_union(value).wkb
            adm_level[key] = value[0].wkb

        df = pd.DataFrame.from_dict(adm_level, orient="index", columns=["geom"])

        df.reset_index(inplace=True)

        df.rename(columns={"index": "division_name"}, inplace=True)
        df = df.assign(country_name=model_place, level=lev)

        all_data.append(df)

    if len(all_data):
        all_data = pd.concat(all_data)
        all_data = all_data[["country_name", "division_name", "level", "geom"]]

    return all_data


def add_subdivisions_to_model(project: Project, model_place: str, source: str, levels_to_add=2, overwrite=False):
    """
    Adds subdivisions to model.
    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project
         *model_place*(:obj:`str`): current model place
         *source*(:obj:`str`): data source to import subdivisions. Takes GADM or GeoBoundaries. Default to GADM.
         *levels_to_add(:obj:`int`): number of political subdivisions to add. Defaults to 2.
         *overwrite*(:obj:`bool`): overwrite existing political subdivisions. Defaults to False.
    """
    if source.lower() == "gadm":
        df = get_subdivisions_gadm(model_place, levels_to_add)
    elif source.lower() == "geoboundaries":
        df = get_subdivisions_online(model_place, levels_to_add)
    else:
        raise ValueError("This subdivision source is not available.")

    # Check if subdivisions already exists otherwise create a file with this name
    conn = sqlite3.connect(join("project_database.sqlite"))
    all_tables = [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()]

    if overwrite or "political_subdivisions" not in all_tables:
        project.conn.execute("DELETE FROM political_subdivisions WHERE level>0;")
        project.conn.commit()

        qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
               VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
        list_of_tuples = list(df.itertuples(index=False, name=None))

        project.conn.executemany(qry, list_of_tuples)
        project.conn.commit()
