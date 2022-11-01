from aequilibrae import Project, Parameters

from tradesman.data_retrieval.country_main_area import country_border_from_model
from tradesman.model_creation.extra_data_fields import extra_fields


def import_network(project: Project, model_place: str):
    """Imports network from"""
    par = Parameters()
    par.parameters["network"]["links"]["fields"]["one-way"].extend(extra_fields)
    par.write_back()

    project.network.create_from_osm(place_name=model_place)

    # place_geo = country_border_from_model(project)
    # if place_geo.area == 0:
    #     raise Warning("No country borders were imported.")
    # else:
    #     sql = """DELETE from Links
    #                          WHERE link_id not in (SELECT a.link_id
    #                                                FROM links AS a, political_subdivisions as b
    #                                                WHERE ST_Intersects(a.geometry, ST_Buffer(b.geometry, 0.1)) = 1)"""
    #     """DELETE * FROM Links
    #             WHERE link_id NOT IN (SELECT a.link_id
    #                                    FROM links AS a, (SELECT ST_Buffer(geometry, 0.1) geometry
    #                                                             FROM political_subdivisions
    #                                                             WHERE level=0) as b
    #                                    WHERE ST_Intersects(a.geometry, b.geometry) = 1)"""
    #
    #     project.conn.execute(sql)
    #     project.conn.commit()
