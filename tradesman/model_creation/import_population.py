from aequilibrae import Project

from tradesman.data.population_file_address import link_source
from tradesman.data.population_raster import population_raster


def import_population(project: Project, model_place: str, source: str, overwrite=False):
    if sum(project.conn.execute("Select count(*) from raw_population").fetchone()) > 0:
        if not overwrite:
            return
        project.conn.execute("DELETE FROM raw_population;")

    url = link_source(model_place, source)

    if url == "no file":
        raise ValueError("Could not find a population file to import")

    df = population_raster(url, f"pop_{model_place}", project)

    df.to_sql("raw_population", project.conn, if_exists="append", index=False)
    project.conn.execute("UPDATE raw_population SET Geometry=MakePoint(longitude, latitude, 4326)")
    project.conn.commit()
