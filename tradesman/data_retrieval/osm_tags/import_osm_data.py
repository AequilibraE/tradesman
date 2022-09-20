import sqlite3
import numpy as np
from os.path import join
from shapely.geometry import Point, Polygon
import pandas as pd
import geopandas as gpd
from aequilibrae import Project
from tradesman.data.load_zones import load_zones
from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag
from tradesman.data_retrieval.osm_tags.osm_tag_values import (
    building_values,
    amenity_values,
)
from shapely import wkb


def import_osm_data(tag: str, osm_data: dict, project: Project, tile_size=25):
    """
    Import and save OSM amenity or building data to project.

    Parameters:
         *tag*(:obj:`str`): download objects from Open Street Maps. Takes amenity or buildings.
         *osm_data*(:obj:`dict`): store downloaded data.
         *project*(:obj:`aequilibrae.project): current project.
         *tile_size*(:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side.
    """

    if tag == "building":
        df = pd.DataFrame.from_dict(generic_tag(tag, osm_data, project, tile_size))
        tag_value = building_values
    elif tag == "amenity":
        df = pd.DataFrame.from_dict(generic_tag(tag, osm_data, project, tile_size))
        tag_value = amenity_values
    else:
        raise ValueError(f"No data with {tag} tag was imported.")

    df["geom"] = df.apply(point_or_polygon, axis=1)

    tags = df["tags"].apply(pd.Series)[[tag]]

    tags[f"update_{tag}"] = tags[tag].apply(lambda x: tag_value.get(x))

    tags[f"update_{tag}"].fillna(value="others", inplace=True)

    tags.drop(columns=[tag], inplace=True)

    tags.rename(columns={f"update_{tag}": tag}, inplace=True)

    merged_df = df.merge(tags, left_index=True, right_index=True)[["type", "id", "geom", tag]]

    gdf = gpd.GeoDataFrame(merged_df, geometry=gpd.GeoSeries.from_wkb(merged_df.geom), crs=4326)

    zones = load_zones(project)

    tag_by_zone = gpd.sjoin(gdf, zones)

    tag_by_zone.drop(columns="index_right", inplace=True)

    all_tables = [x[0] for x in project.conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()]

    if tag == "building" and "osm_buildings" not in all_tables:
        saving_buildings(tag_by_zone, project)
    elif tag == "amenity" and "osm_amenities" not in all_tables:
        saving_amenities(tag_by_zone, project)

    return tag_by_zone


def point_or_polygon(row):
    """
    Write the WKB of a Point or a Polygon.

    Parameters:
         *row*(:obj:`pd.DataFrame`): rows of a pandas' DataFrame.
    """
    if row.type == "node":

        return Point(np.array([row.lon, row.lat])).wkb

    else:

        poly = []
        for dct in row.geometry:
            poly.append((dct["lon"], dct["lat"]))

        return Polygon(poly).wkb


def saving_buildings(tag_by_zone, project):
    """
    Saves OSM building information.

    Parameters:
         *tag_by_zone*(:obj:`gpd.GeoDataFrame`): GeoDataFrame containing tag information by zone.
         *project*(:obj:`aequilibrae.project): current project.
    """
    tag_by_zone["area"] = tag_by_zone.to_crs(3857).area
    list_of_tuples = list(
        tag_by_zone[["type", "id", "building", "zone_id", "area", "geom"]].fillna(0).itertuples(index=False, name=None)
    )
    qry = "INSERT into osm_buildings(type, id, building, zone_id, area, geometry) VALUES(?, ?, ?, ?, ?, CastToMultiPolygon(ST_GeomFromWKB(?, 4326)));"
    print("Saving OSM buildings.")
    project.conn.execute(
        'CREATE TABLE IF NOT EXISTS osm_buildings("type" TEXT, "id" INTEGER, "building" TEXT, "zone_id" INTEGER,\
                                                                    "area" FLOAT);'
    )

    project.conn.execute("SELECT AddGeometryColumn('osm_buildings', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );")
    project.conn.execute("SELECT CreateSpatialIndex('osm_buildings', 'geometry' );")
    project.conn.commit()

    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()


def saving_amenities(tag_by_zone, project):
    """
    Saves OSM amenity information.

    Parameters:
         *tag_by_zone*(:obj:`gpd.GeoDataFrame`): GeoDataFrame containing tag information by zone.
         *project*(:obj:`aequilibrae.project): current project.
    """
    qry = "INSERT into osm_amenities(type, id, amenity, zone_id, geometry) VALUES(?, ?, ?, ?, CastToPoint(GeomFromWKB(?, 4326)));"
    list_of_tuples = list(
        tag_by_zone[["type", "id", "amenity", "zone_id", "geom"]].fillna(0).itertuples(index=False, name=None)
    )
    print("Saving OSM amenities.")
    project.conn.execute(
        'CREATE TABLE IF NOT EXISTS osm_amenities("type" TEXT, "id" INTEGER, "amenity" TEXT, "zone_id" INTEGER);'
    )

    project.conn.execute("SELECT AddGeometryColumn('osm_amenities', 'geometry', 4326, 'POINT', 'XY' );")
    project.conn.execute("SELECT CreateSpatialIndex('osm_amenities', 'geometry' );")
    project.conn.commit()

    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()
