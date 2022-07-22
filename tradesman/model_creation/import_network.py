from aequilibrae import Project, Parameters

from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.extra_data_fields import extra_fields


def import_network(project: Project, model_place: str):
    par = Parameters()
    par.parameters["network"]["links"]["fields"]["one-way"].extend(extra_fields)
    par.write_back()

    project.network.create_from_osm(place_name=model_place)

    place_geo = add_country_borders_to_model(country_name=model_place, project=project)
    if place_geo.area == 0:
        raise Warning("No country borders were imported.")

    sql = """DELETE from Links where link_id not in (SELECT a.link_id
                                                            FROM links AS a, country_borders as b
                                                            WHERE ST_Intersects(a.geometry, b.geometry) = 1)"""

    project.conn.execute(sql)
    project.conn.commit()
