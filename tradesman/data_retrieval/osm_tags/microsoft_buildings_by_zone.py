from tempfile import gettempdir
from os.path import join
import geopandas as gpd
from aequilibrae import Project
import numpy as np

from tradesman.data.load_zones import load_zones
from tradesman.data_retrieval.osm_tags.microsoft_download_file import microsoft_download_file


def microsoft_buildings_by_zone(model_place: str, project: Project):
    """
    Download and saves in project informations from Microsoft Bing buildings.

    Parameters:
         *model_palce*(:obj:`str`): current model place
         *project*(:obj:`aequilibrae.project): current project
    """

    microsoft_download_file(model_place)

    model_gdf = gpd.read_file(join(gettempdir(), f"{model_place}.geojsonl"))

    model_gdf["area"] = model_gdf.to_crs(3857).geometry.area

    zones = load_zones(project)

    buildings_by_zone = gpd.sjoin(model_gdf, zones)

    buildings_by_zone.drop(columns=["index_right"], inplace=True)

    buildings_by_zone.insert(0, column="id", value=np.arange(1, len(buildings_by_zone) + 1))

    buildings_by_zone["geom"] = buildings_by_zone.geometry.to_wkb()

    print("Saving Microsoft buildings.")

    project.conn.execute("DROP TABLE IF EXISTS microsoft_buildings;")
    project.conn.execute(
        'CREATE TABLE IF NOT EXISTS microsoft_buildings("id" INTEGER, "area" FLOAT, "zone_id" INTEGER);'
    )
    project.conn.execute("SELECT AddGeometryColumn('microsoft_buildings', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );")

    project.conn.execute("SELECT CreateSpatialIndex( 'microsoft_buildings' , 'geometry' );")
    project.conn.commit()

    qry = """INSERT INTO microsoft_buildings(id, area, zone_id, geometry) VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"""
    list_of_tuples = list(buildings_by_zone[["id", "area", "zone_id", "geom"]].itertuples(index=False, name=None))
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()

    return buildings_by_zone
