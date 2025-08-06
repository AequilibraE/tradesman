import geopandas as gpd
from aequilibrae import Project

from tradesman.data.population_file_address import link_source
from tradesman.data.population_raster import population_raster


def import_population(project: Project, country_name: str, source: str, overwrite=False):
    """
    Imports population information into the model.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
        *country_name*(:obj:`str`): model place country
        *source*(:obj:`str`): database source to download population data. Defaults to WorldPop
        *overwrite*(:obj:`bool`): overwrites existing raw_population info from the model. Defaults to False
    """
    with project.db_connection as conn:
        if sum(conn.execute("Select count(*) from raw_population").fetchone()) > 0:
            if not overwrite:
                return
            conn.execute("DELETE FROM raw_population;")

        url = link_source(country_name, source)

        if url == "no file":
            raise ValueError("Could not find a population file to import")

        df = population_raster(url, f"pop_{country_name}", project)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)

        model_area = gpd.read_postgis(
            "SELECT ST_AsBinary(geometry) as geom FROM political_subdivisions WHERE level=-1", con=conn, crs=4326
        )

        select_pop = gdf.clip(model_area, keep_geom_type=True)[["longitude", "latitude", "population"]]

        select_pop.to_sql("raw_population", conn, if_exists="append", index=False)
        conn.execute("UPDATE raw_population SET Geometry=MakePoint(longitude, latitude, 4326)")
