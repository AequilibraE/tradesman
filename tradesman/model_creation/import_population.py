from aequilibrae import Project, Parameters
import sqlite3

from tradesman.data.population_file_address import link_source
from tradesman.data.population_raster import population_raster


def import_population(project: Project, model_place: str, source: str, overwrite=False):

    if "raw_population" in [
        x[0] for x in project.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]:
        print("raw_population file will be overwritten.")
        project.conn.execute("Drop table if exists raw_population")
        project.conn.commit()

    else:
        pass

    url = link_source(model_place, source)

    if url == "no file":
        raise ValueError

    df = population_raster(url, f"pop_{model_place}", project)

    project.conn.execute("Drop table if exists raw_population")
    project.conn.commit()

    df.to_sql("raw_population", project.conn, if_exists="replace", index=False)
    project.conn.execute("select AddGeometryColumn( 'raw_population', 'geometry', 4326, 'POINT', 'XY', 1);")
    project.conn.execute("UPDATE raw_population SET Geometry=MakePoint(longitude, latitude, 4326)")
    project.conn.execute("SELECT CreateSpatialIndex( 'raw_population' , 'geometry' );")
    project.conn.commit()
