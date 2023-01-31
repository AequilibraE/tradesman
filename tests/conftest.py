import os
import shutil
from uuid import uuid4
import pytest
from aequilibrae.project import Project

from aequilibrae.utils.create_example import create_example
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
def nauru_test(create_path):
    prj = create_example(create_path, "nauru")
    add_new_tables(prj.conn)

    shutil.copy(
        os.path.join(os.path.dirname(__file__), "data/nauru/Nauru_cache_gadm.parquet"),
        os.path.join(create_path, "Nauru_cache_gadm.parquet"),
    )

    data = ImportPoliticalSubdivisions(model_place="Nauru", project=prj, source="GADM")
    data.import_model_area()
    data.add_country_borders()
    data.import_subdivisions(2)

    yield prj
    prj.close()
