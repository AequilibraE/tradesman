import json
import requests
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
from shapely import wkt


def get_subdivisions(model_place: str, level: int):

    pop_path = "/home/jovyan/workspace/road_analytics/tradesman/data/population/all_raster_pop_source.csv"
    df = pd.read_csv(pop_path)
    iso_code = df[df.Country.str.upper() == model_place.upper()].iso_country.values[0]

    r = requests.get(f"https://www.geoboundaries.org/gbRequest.html?ISO={iso_code}&ADM=ADM{level}")

    if len(r.json()) > 0:
        dlPath = r.json()[0]["gjDownloadURL"]
        geoBoundary = requests.get(dlPath).json()

    else:
        print(f"There is no administrative boundary level {level}. Will use administrative boundary level 1 instead.")
        r = requests.get(f"https://www.geoboundaries.org/gbRequest.html?ISO={iso_code}&ADM=ADM1")
        dlPath = r.json()[0]["gjDownloadURL"]
        geoBoundary = requests.get(dlPath).json()

    adm_level = {}

    for boundary in geoBoundary["features"]:

        if not boundary["properties"]["shapeName"] in adm_level:
            adm_level[boundary["properties"]["shapeName"]] = []

        if boundary["geometry"]["type"] == "MultiPolygon":
            polys = boundary["geometry"]["coordinates"]
            for poly in polys:
                adm_level[boundary["properties"]["shapeName"]].append(Polygon(poly[0]))
        else:
            adm_level[boundary["properties"]["shapeName"]].append(Polygon(boundary["geometry"]["coordinates"][0]))

    for key, value in adm_level.items():
        adm_level[key] = unary_union(value).wkt

    df = pd.DataFrame.from_dict(adm_level, orient="index", columns=["geometry"])

    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df.geometry), crs=4326)

    gdf.insert(0, "level", level)
    gdf.insert(1, "country_name", model_place)

    return gdf
