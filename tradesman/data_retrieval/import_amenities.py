from aequilibrae import Project
import numpy as np

from tradesman.data_retrieval.osm_tags.import_osm_data import import_osm_data
from tradesman.data_retrieval.osm_tags.query_writer import amenity_count_query


def import_amenities(model_place: str, project: Project, osm_data: dict):

    osm_amenities = import_osm_data(tag="amenity", model_place=model_place, osm_data=osm_data, project=project)

    count_amenities = osm_amenities.groupby(["amenity", "zone_id"]).count()[["type"]].unstack().transpose()
    count_amenities["zone_id"] = np.arange(1, max(osm_amenities.zone_id) + 1)

    for col in osm_amenities.amenity.unique():
        exp = f"ALTER TABLE zones ADD osm_{col}_amenity INT;"
        project.conn.execute(exp)
        project.conn.commit()

    qry = amenity_count_query(count_amenities, func="set_zero")
    project.conn.executemany(qry, list((x,) for x in count_amenities.zone_id))
    project.conn.commit()

    qry = amenity_count_query(count_amenities)
    project.conn.executemany(qry, list(count_amenities.itertuples(index=False, name=None)))
    project.conn.commit()
