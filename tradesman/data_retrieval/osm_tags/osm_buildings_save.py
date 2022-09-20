from numpy import arange
from aequilibrae.project import Project

from tradesman.data_retrieval.osm_tags.query_writer import building_area_query, building_count_query


def save_osm_buildings(osm_buildings, project: Project):
    """
    Save OSM building counts and area by type in each project zone.

    Parameters:
         *osm_buildings*(:obj:`gpd.GeoDataFrame`): GeoDataFrame containing OSM building information.
         *project*(:obj:`aequilibrae.project): current project.
    """

    count_osm_buildings = osm_buildings.groupby(["building", "zone_id"]).count()[["type"]].unstack().transpose()
    count_osm_buildings["zone_id"] = arange(1, max(osm_buildings.zone_id) + 1)

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
    area_osm_buildings["zone_id"] = arange(1, max(osm_buildings.zone_id) + 1)

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
