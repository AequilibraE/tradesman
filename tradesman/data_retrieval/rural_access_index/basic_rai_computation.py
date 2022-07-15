import pandas as pd
import geopandas as gpd
from tradesman.data.load_zones import load_zones
from geopandas import sjoin_nearest

from tradesman.data_retrieval.rural_access_index.population_data import population_data


def basic_RAI_data(project):

    # print('Obtaining population data')
    pop_data = population_data(project).to_crs(3857)

    # print('Obtaining network data')
    links = project.network.links.data
    links = links[links.modes.str.contains("c")]
    links = gpd.GeoDataFrame(links[["link_id", "geometry"]], geometry="geometry", crs=4326).to_crs(3857)

    # print('Computing population distance to network')
    df = sjoin_nearest(pop_data, links, distance_col="distance_to_link")
    df.drop(columns=["index_right"], inplace=True)

    df["accessible"] = df.population
    df.loc[df.distance_to_link > 2000, "accessible"] = 0
    df["inaccessible"] = df.population
    df.loc[df.distance_to_link <= 2000, "inaccessible"] = 0

    df.to_crs(4326, inplace=True)

    # Add subdivision info
    # print('Obtaining country subdivisions')
    sql = "SELECT division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM country_subdivisions;"
    subdivisions = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)
    subdivisions = subdivisions[subdivisions.level == subdivisions.level.max()]

    df = gpd.sjoin(df, subdivisions)
    df.drop(columns=["index_right"], inplace=True)

    # Add zone data
    # print('Obtaining model zones')
    zones = load_zones(project)[["zone_id", "geometry"]]
    gdf = gpd.sjoin(df, zones)
    gdf.drop(columns=["index_right", "distance_to_link", "link_id"], inplace=True)

    return gdf
