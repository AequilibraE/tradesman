from time import sleep
import requests
from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


def load_osm_data(tag: str, osm_data: dict, tile_size, queries, model_place: str):

    """Loads data from OSM or cached to disk"""

    if tag not in osm_data:
        osm_data[tag] = []

    url = "http://overpass-api.de/api/interpreter"

    # We won't download any area bigger than 25km by 25km
    bboxes = bounding_boxes(model_place, tile_size)

    http_headers = requests.utils.default_headers()
    http_headers.update({"Accept-Language": "en", "format": "json"})

    for query in queries:
        for bbox in bboxes:
            bbox_str = ",".join([str(round(x, 6)) for x in bbox])
            data = {"data": query.format(bbox_str)}
            response = requests.post(url, data=data, timeout=180, headers=http_headers)
            if response.status_code != 200:
                # raise ConnectionError("Could not download data")
                sleep(2)
                continue

            # get the response size and the domain, log result
            json = response.json()
            if "elements" in json:
                elements = json["elements"]
                valid_elements = [x for x in elements if x.get("tags", {})]
                osm_data[tag].extend(valid_elements)
            sleep(2)

    return osm_data
