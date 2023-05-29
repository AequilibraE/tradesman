import re
from os.path import isfile, join
from tempfile import gettempdir
from urllib.request import urlretrieve

import geopandas as gpd
import pandas as pd
import pycountry
import requests
from aequilibrae.project import Project
from aequilibrae.project.project_creation import add_triggers, remove_triggers
from shapely.geometry import Polygon


def get_maritime_boundaries(model_place: str):
    """
    Import maritime boundaries from countries. If country has no maritime boundary, it returns None.

    Parameters:
         *model_place*(:obj:`str`): current model place
    """
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    url = "https://github.com/AequilibraE/tradesman/releases/download/V0.1b/maritime_boundaries.gpkg"

    dest_path = join(gettempdir(), "maritime_boundaries.gpkg")

    if not isfile(dest_path):
        urlretrieve(url, dest_path)

    gdf = gpd.read_file(dest_path)

    if country_code in gdf.ISO_TER1.values:
        return gdf[gdf.ISO_TER1 == country_code]
    return


def place_is_country(model_place: str):
    """
    Checks if model_place is a country.

    Parameters:
         *model_place*(:obj:`str`): current model place
    """
    search_place = model_place.lower().replace(" ", "+")

    nom_url = (
        f"https://nominatim.openstreetmap.org/search?q={search_place}&format=json&addressdetails=1&accept-language=en"
    )

    r = requests.get(nom_url)

    country_name = pycountry.countries.search_fuzzy(r.json()[0]["address"]["country"])[0].name

    if re.search(model_place, country_name):
        return True
    return False


def delete_links_and_nodes(model_place, project: Project):
    """
    Removes links and nodes outside the political subdivision.

    Parameters:
         *model_place*(:obj:`str`): current model place
         *project*(:obj:`aequilibrae.project.Project`): currently open project
    """

    if not place_is_country(model_place):
        return

    coast = get_maritime_boundaries(model_place)

    sql = "SELECT country_name, division_name, level, Hex(ST_AsBinary(GEOMETRY)) geometry FROM political_subdivisions WHERE level=0;"

    borders = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geometry", crs=4326).explode(index_parts=True)

    if coast is None:
        gdf_country_boundary = borders.copy()

    else:
        coast = coast.explode(index_parts=True)

        exploded_gdf = coast.overlay(borders, how="union").dissolve().explode(index_parts=True)

        get_border_linearring = pd.DataFrame(
            [Polygon(exploded_gdf.exterior.values[i]) for i in range(len(exploded_gdf))], columns=["geom"]
        )

        gdf_country_boundary = gpd.GeoDataFrame(get_border_linearring, geometry=get_border_linearring.geom, crs=4326)

    links_query = "SELECT link_id, Hex(ST_AsBinary(GEOMETRY)) geometry FROM links;"

    links = gpd.GeoDataFrame.from_postgis(links_query, project.conn, geom_col="geometry", crs=4326)

    inner_gdf = gpd.sjoin(gdf_country_boundary, links, how="inner")

    del_links = list(links[~links.link_id.isin(inner_gdf.link_id)][["link_id"]].itertuples(index=False, name=None))

    remove_triggers(project.conn, project.logger, "network")

    project.conn.executemany("DELETE FROM links WHERE link_id=?", del_links)
    project.conn.commit()

    nodes_query = """DELETE FROM nodes
    WHERE node_id NOT IN (SELECT a_node FROM links
                        UNION ALL
                                        SELECT b_node FROM links);
    """

    project.conn.execute(nodes_query)
    project.conn.commit()

    add_triggers(project.conn, project.logger, "network")
