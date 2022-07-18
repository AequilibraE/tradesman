import sqlite3
from os.path import join

from aequilibrae import Project

from tradesman.model_creation.get_country_subdivision import get_subdivisions


def add_subdivisions_to_model(project: Project, model_place: str, levels_to_add=2, overwrite=True):
    gdf = get_subdivisions(model_place, levels_to_add)

    # Check if subdivisions already exists otherwise create a file with this name
    conn = sqlite3.connect(join("project_database.sqlite"))
    all_tables = [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()]

    if overwrite or "country_subdivisions" not in all_tables:
        project.conn.execute("DROP TABLE IF EXISTS country_subdivisions;")
        project.conn.execute('CREATE TABLE IF NOT EXISTS country_subdivisions("division_name" TEXT, "level" INTEGER);')
        project.conn.execute(
            "SELECT AddGeometryColumn('country_subdivisions', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );"
        )
        project.conn.execute("SELECT CreateSpatialIndex('country_subdivisions' , 'geometry' );")
        project.conn.commit()

        qry = "INSERT INTO country_subdivisions (division_name, level, geometry) VALUES(?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
        list_of_tuples = [(x, y, z) for x, y, z in zip(gdf.index, gdf.level, gdf.geometry.to_wkb())]

        project.conn.executemany(qry, list_of_tuples)
        project.conn.commit()
