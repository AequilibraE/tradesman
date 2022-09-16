from aequilibrae import Project
import numpy as np

from tradesman.data_retrieval.osm_tags.import_osm_data import import_osm_data
from tradesman.data_retrieval.osm_tags.microsoft_buildings_by_zone import (
    microsoft_buildings_by_zone,
)
from tradesman.data_retrieval.osm_tags.query_writer import building_area_query, building_count_query


def building_import(model_place: str, project: Project, osm_data: dict):

    microsoft_buildings = microsoft_buildings_by_zone(model_place, project)

    if microsoft_buildings is None:
        pass

    else:

        project.conn.execute("ALTER TABLE zones ADD microsoft_building_count INT;")
        project.conn.commit()

        project.conn.execute("ALTER TABLE zones ADD microsoft_building_area FLOAT;")
        project.conn.commit()

        list_of_tuples = list(
            zip(
                microsoft_buildings.groupby("zone_id").count().id.values,
                microsoft_buildings.groupby("zone_id").sum().area.values,
                np.arange(1, max(microsoft_buildings.zone_id) + 1),
            )
        )

        project.conn.execute(
            "UPDATE zones SET microsoft_building_area=0, microsoft_building_count=0 WHERE microsoft_building_count IS NULL;"
        )
        project.conn.commit()

        qry = "UPDATE zones SET microsoft_building_count=?, microsoft_building_area=? WHERE zone_id=?;"
        project.conn.executemany(qry, list_of_tuples)
        project.conn.commit()

    osm_buildings = import_osm_data(tag="building", model_place=model_place, osm_data=osm_data, project=project)

    count_osm_buildings = osm_buildings.groupby(["building", "zone_id"]).count()[["type"]].unstack().transpose()
    count_osm_buildings["zone_id"] = np.arange(1, max(osm_buildings.zone_id) + 1)

    for col in count_osm_buildings.columns[:-1]:
        exp = f"ALTER TABLE zones ADD osm_{col}_building INT;"
        project.conn.execute(exp)
        project.conn.commit()

    qry = building_count_query(count_osm_buildings, func="set_zero")
    project.conn.executemany(qry, list((x,) for x in count_osm_buildings.zone_id))
    project.conn.commit()

    qry = building_count_query(count_osm_buildings)
    project.conn.executemany(qry, list(count_osm_buildings.itertuples(index=False, name=None)))
    project.conn.commit()

    area_osm_buildings = osm_buildings.groupby(["building", "zone_id"]).sum()[["area"]].unstack().transpose()
    area_osm_buildings["zone_id"] = np.arange(1, max(osm_buildings.zone_id) + 1)

    for col in area_osm_buildings.columns[:-1]:
        exp = f"ALTER TABLE zones ADD osm_{col}_building_area FLOAT;"
        project.conn.execute(exp)
        project.conn.commit()

    qry = building_area_query(area_osm_buildings, func="set_zero")
    project.conn.executemany(qry, list((x,) for x in area_osm_buildings.zone_id))
    project.conn.commit()

    qry = building_area_query(area_osm_buildings)
    project.conn.executemany(qry, list(area_osm_buildings.itertuples(index=False, name=None)))
    project.conn.commit()
