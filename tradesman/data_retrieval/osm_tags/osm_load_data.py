import bz2
import geopandas as gpd
import hashlib
from os.path import isfile, join
import pickle
from tempfile import gettempdir
from time import sleep
import requests
from aequilibrae.project import Project
from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


def load_osm_data(tag: str, osm_data: dict, tile_size, queries, project: Project):
    """
    Loads data from OSM or cached to disk.

    Parameters:
         *tag*(:obj:`str`): download objects from Open Street Maps. Takes amenity or buildings.
         *osm_data*(:obj:`dict`): store downloaded data.
         *tile_size*(:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side.
         *queries*(:obj:`str`): SQL queries to request Overpass API.
         *project*(:obj:`aequilibrae.project): current project.
    """

    if osm_data.get(tag, {}):
        osm_data[tag] = []
    else:
        if tag not in osm_data:
            osm_data[tag] = []

    cache_name = __cache_name(tag, project)
    if isfile(cache_name):
        osm_data[tag] = __load_cache(cache_name)[tag]
        return

    url = "http://overpass-api.de/api/interpreter"

    bboxes = bounding_boxes(project, tile_size)

    http_headers = requests.utils.default_headers()
    http_headers.update({"Accept-Language": "en", "format": "json"})

    for query in queries:
        for bbox in bboxes:
            bbox_str = ",".join([str(round(x, 6)) for x in bbox])
            data = {"data": query.format(bbox_str)}
            response = requests.post(url, data=data, timeout=180, headers=http_headers)
            if response.status_code != 200:
                continue

            json = response.json()
            if "elements" in json:
                elements = json["elements"]
                valid_elements = [x for x in elements if x.get("tags", {})]
                osm_data[tag].extend(valid_elements)
            sleep(2)

    with bz2.BZ2File(cache_name, "wb") as f:
        pickle.dump(osm_data, f)

    return osm_data


def __cache_name(element: str, project: Project):
    """
    Create memory cache to store data.

    Parameters:
         *element*(:obj:`str`): objects downloaded from Open Street Maps. Takes amenity or buildings.
         *project*(:obj:`aequilibrae.project): current project.
    """

    sql_coverage = "SELECT Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where level=0;"
    coverage_area = gpd.GeoDataFrame.from_postgis(sql_coverage, project.conn, geom_col="geometry", crs=4326)
    area_bounds = coverage_area.bounds.values
    m = hashlib.md5()
    m.update(element.encode())
    m.update("".join([str(x) for x in area_bounds]).encode())

    return join(gettempdir(), f"{m.hexdigest()}.pkl")


def __load_cache(cache_name):
    """
    Load data cached to memory.

    Parameters:
         *cache_name*: cache file name
    """
    with bz2.BZ2File(cache_name, "rb") as f:
        return pickle.load(f)
