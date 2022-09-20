from numpy import arange
from aequilibrae.project import Project


def save_microsoft_buildings(microsoft_buildings, project: Project):
    """
    Save Microsoft Bing building counts and area in each project zone.

    Parameters:
         *microsoft_buildings*(:obj:`gpd.GeoDataFrame`): GeoDataFrame containing Microsoft Bing information.
         *project*(:obj:`aequilibrae.project): current project
    """

    project.conn.execute("ALTER TABLE zones ADD microsoft_building_count INT;")
    project.conn.commit()

    project.conn.execute("ALTER TABLE zones ADD microsoft_building_area FLOAT;")
    project.conn.commit()

    list_of_tuples = list(
        zip(
            microsoft_buildings.groupby("zone_id").count().id.values,
            microsoft_buildings.groupby("zone_id").sum().area.values,
            arange(1, max(microsoft_buildings.zone_id) + 1),
        )
    )

    project.conn.execute(
        "UPDATE zones SET microsoft_building_area=0, microsoft_building_count=0 WHERE microsoft_building_count IS NULL;"
    )
    project.conn.commit()

    qry = "UPDATE zones SET microsoft_building_count=?, microsoft_building_area=? WHERE zone_id=?;"
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()
