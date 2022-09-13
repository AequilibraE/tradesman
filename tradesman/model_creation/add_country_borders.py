import geopandas as gpd
import pandas as pd
import urllib.request
from os.path import join, isfile
from tempfile import gettempdir
import pycountry
import requests
from shapely.geometry import Polygon, MultiPolygon


def get_borders_gadm(model_place: str):
    """
    Import country borders from GADM.
    Parameters:
         *model_place*(:obj:`str`): current model place
    """
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{country_code}.gpkg"

    dest_path = join(gettempdir(), f"gadm_{country_code}.gpkg")
    if not isfile(dest_path):
        urllib.request.urlretrieve(url, dest_path)

    level0 = gpd.read_file(dest_path, layer="ADM_ADM_0")
    level0 = level0.assign(level=0, division_name="country_border")
    level0["geom"] = gpd.GeoSeries.to_wkb(level0.geometry)
    level0.rename(columns={"COUNTRY": "country"}, inplace=True)

    return level0.geom.values[0]


def get_borders_online(model_place: str):
    """
    Import country borders from GeoBoundaries.
    Parameters:
         *model_place*(:obj:`str`): current model place
    """
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    r = requests.get(f"https://www.geoboundaries.org/gbRequest.html?ISO={country_code}&ADM=ADM0")
    dlPath = r.json()[0]["gjDownloadURL"]
    geoBoundary = requests.get(dlPath).json()
    if not geoBoundary["features"]:
        return MultiPolygon([0])
    geo = geoBoundary["features"][0]["geometry"]

    return MultiPolygon([Polygon(poly[0]) for poly in geo["coordinates"]]).wkb


def add_country_borders_to_model(model_place: str, project, overwrite=False, source="gadm"):
    """
    Import and add country borders to model.
    Parameters:
         *model_place*(:obj:`str`): current model place
         *project*(:obj:`aequilibrae.project`): currently open project
         *overwrite*(:obj:`bool`): overwrite existing country borders. Defaults to False.
         *source*(:obj:`str`): data source to import subdivisions. Takes GADM or GeoBoundaries. Defaults to GADM.
    """
    project.conn.execute('CREATE TABLE IF NOT EXISTS political_subdivisions("country_name" TEXT);')

    if not overwrite:
        if sum(project.conn.execute("SELECT count(*) FROM political_subdivisions where level=0").fetchone()) > 0:
            return

    if source.lower() == "gadm":
        geo = get_borders_gadm(model_place)
    elif source.lower() == "geoboundaries":
        geo = get_borders_online(model_place)
    else:
        raise ValueError("This country border source is not available.")

    project.conn.execute("DELETE FROM political_subdivisions where level=0;")
    project.conn.commit()

    sql = """INSERT into political_subdivisions(country_name, division_name, level, geometry)
                         VALUES(?, "country_border", 0, CastToMulti(GeomFromWKB(?, 4326)));"""
    project.conn.execute(sql, [model_place, geo])
    project.conn.commit()
