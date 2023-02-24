import os
import shutil
from uuid import uuid4
import pytest
from aequilibrae.project import Project
import geopandas as gpd

from aequilibrae.utils.create_example import create_example
from tradesman.data.population_file_address import link_source
from tradesman.data.population_raster import population_raster
from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions


@pytest.fixture
def create_path(tmp_path):
    return os.path.join(tmp_path, uuid4().hex)


@pytest.fixture
def empty_aequilibrae_model(create_path):
    prj = Project()
    prj.new(create_path)

    add_new_tables(prj.conn)
    yield prj
    prj.close()


@pytest.fixture
def network_connection(empty_aequilibrae_model):
    yield empty_aequilibrae_model.conn


@pytest.fixture
def nauru_test(create_path, tmp_path):
    prj = create_example(create_path, "nauru")
    add_new_tables(prj.conn)

    shutil.copy(
        os.path.join(os.path.dirname(__file__), "data/nauru/Nauru_cache_gadm.parquet"),
        os.path.join(tmp_path, "Nauru_cache_gadm.parquet"),
    )

    data = ImportPoliticalSubdivisions(model_place="Nauru", project=prj, source="GADM")
    data.import_model_area()
    data.add_country_borders()
    data.import_subdivisions(2)

    yield prj
    prj.close()


@pytest.fixture
def nauru_pop_test(nauru_test, create_path, tmp_path):
    shutil.copy(
        os.path.join(os.path.dirname(__file__), "data/nauru/pop_Nauru.tif"),
        os.path.join(tmp_path, "pop_Nauru.tif"),
    )

    url = link_source("Nauru", "WorldPop")

    df = population_raster(url, "pop_Nauru", nauru_test)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)

    model_area = gpd.read_postgis(
        "SELECT ST_AsBinary(geometry) as geom FROM political_subdivisions WHERE level=-1", con=nauru_test.conn, crs=4326
    )

    select_pop = gdf.clip(model_area, keep_geom_type=True)[["longitude", "latitude", "population"]]

    select_pop.to_sql("raw_population", nauru_test.conn, if_exists="append", index=False)
    nauru_test.conn.execute("UPDATE raw_population SET Geometry=MakePoint(longitude, latitude, 4326)")
    nauru_test.conn.commit()

    yield nauru_test
