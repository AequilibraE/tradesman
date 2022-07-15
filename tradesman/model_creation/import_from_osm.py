from aequilibrae import Project, Parameters

from tradesman.model_creation.country_borders import get_country_borders


def import_net_from_osm(project: Project, model_place: str):
    new_fields = [
        {
            "bridge": {
                "description": "bridge flag",
                "osm_source": "bridge",
                "type": "text",
            }
        },
        {
            "tunnel": {
                "description": "tunnel flag",
                "osm_source": "tunnel",
                "type": "text",
            }
        },
        {"toll": {"description": "toll flag", "osm_source": "toll", "type": "text"}},
        {
            "surface": {
                "description": "pavement surface",
                "osm_source": "surface",
                "type": "text",
            }
        },
    ]

    par = Parameters()
    par.parameters["network"]["links"]["fields"]["one-way"].extend(new_fields)
    par.write_back()

    project.network.create_from_osm(place_name=model_place)

    place_geo = get_country_borders(model_place)

    if place_geo.area == 0:
        raise Warning("No country borders were imported.")

    # Mudar aqui
    project.conn.execute('CREATE TABLE IF NOT EXISTS country_borders("country_name" TEXT);')
    project.conn.execute("SELECT AddGeometryColumn( 'country_borders', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );")

    project.conn.execute("SELECT CreateSpatialIndex( 'country_borders' , 'geometry' );")
    project.conn.commit()

    sql = "INSERT into country_borders(country_name, geometry) VALUES(?, CastToMulti(GeomFromWKB(?, 4326)));"
    project.conn.execute(sql, [model_place, place_geo.wkb])
    project.conn.commit()

    sql = """DELETE from Links where link_id not in (SELECT a.link_id
                                                     FROM links AS a, country_borders as b
                                                     WHERE ST_Intersects(a.geometry, b.geometry) = 1)"""

    project.conn.execute(sql)
    project.conn.commit()
