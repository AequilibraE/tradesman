from aequilibrae import Project
import pandas as pd
import geopandas as gpd

# from tradesman.data_retrieval.osm_building_import import osm_building_import
from tradesman.data_retrieval.osm_tags.import_osm_data import import_osm_data
from tradesman.data_retrieval.osm_tags.microsoft_buildings_by_zone import (
    microsoft_buildings_by_zone,
)
from tradesman.data_retrieval.osm_tags.query_writer import query_writer


def trigger_building_import(model_place: str, project: Project, osm_data: dict):

    zoning = project.zoning
    fields = zoning.fields

    try:
        microsoft_buildings = microsoft_buildings_by_zone(model_place, project)

        fields.add(
            "microsoft_building_count",
            "Number of buildings provided by Microsoft Bing",
            "INTEGER",
        )
        fields.add(
            "microsoft_building_area",
            "Building area provided by Microsoft Bing",
            "FLOAT",
        )

        count_microsoft_buildings = microsoft_buildings.groupby("zone_id").count()
        total_microsoft_area = microsoft_buildings.groupby("zone_id").sum()

        list_of_tuples = [
            (x, y, z)
            for x, y, z in zip(
                count_microsoft_buildings.area,
                total_microsoft_area.area,
                count_microsoft_buildings.index,
            )
        ]

        qry = "UPDATE zones SET microsoft_building_area=0, microsoft_building_count=0 WHERE microsoft_building_count IS NULL;"
        project.conn.execute(qry)
        project.conn.commit()

        qry = "UPDATE zones SET microsoft_building_count=?, microsoft_building_area=? WHERE zone_id=?;"
        project.conn.executemany(qry, list_of_tuples)
        project.conn.commit()

    except ValueError:
        pass

    osm_buildings = import_osm_data(tag="building", model_place=model_place, osm_data=osm_data, project=project)

    count_osm_buildings = osm_buildings.groupby(["building", "zone_id"]).count()
    area_osm_buildings = osm_buildings.groupby(["building", "zone_id"]).sum().round(decimals=2)

    x = count_osm_buildings[["type"]].unstack().transpose().fillna(0)
    x["zone_id"] = [i[1] for i in x.index]

    y = area_osm_buildings[["area"]].unstack().transpose().fillna(0)
    y["zone_id"] = [i[1] for i in y.index]

    for value in osm_buildings.building.unique().tolist():
        fields.add(
            "osm_" + value + "_building",
            "Number of " + value + " buildings provided by OSM",
            "INTEGER",
        )
        fields.add(
            "osm_" + value + "_building_area",
            value + " building area provided by OSM",
            "FLOAT",
        )

    qry = query_writer(count_osm_buildings, tag="building", func="set_value", is_area=False)
    list_of_tuples = list(x.itertuples(index=False, name=None))
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()

    qry = query_writer(area_osm_buildings, tag="building", func="set_value", is_area=True)
    list_of_tuples = list(y.itertuples(index=False, name=None))
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()
