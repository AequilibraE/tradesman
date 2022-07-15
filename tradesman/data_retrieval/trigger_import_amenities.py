from itertools import count
from numpy import safe_eval
import pandas as pd
import sqlite3
from aequilibrae import Project

from tradesman.data_retrieval.osm_tags.import_osm_data import import_osm_data
from tradesman.data_retrieval.osm_tags.query_writer import query_writer


def trigger_import_amenities(model_place: str, project: Project, osm_data: dict):

    osm_amenities = import_osm_data(tag="amenity", model_place=model_place, osm_data=osm_data, project=project)

    zoning = project.zoning
    fields = zoning.fields

    count_amenities = osm_amenities.groupby(["amenity", "zone_id"]).count()
    x = count_amenities[["type"]].unstack().transpose().fillna(0)
    x["zone_id"] = [i[1] for i in x.index]

    for value in osm_amenities.amenity.unique().tolist():
        fields.add(
            "osm_" + value + "_amenity",
            "Number of " + value + " amenities provided by OSM",
            "INTEGER",
        )

    qry = query_writer(count_amenities, tag="amenity", func="set_value", is_area=False)
    list_of_tuples = list(x.itertuples(index=False, name=None))
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()
