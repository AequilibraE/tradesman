import os
import shutil
from uuid import uuid4
import pytest
from aequilibrae.project import Project

from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_population import ImportPopulation


@pytest.fixture
def folder_path(tmp_path):
    return os.path.join(tmp_path, uuid4().hex)


@pytest.fixture
def empty_aequilibrae_model(folder_path):
    prj = Project()
    prj.new(folder_path)

    with prj.db_connection as conn:
        add_new_tables(conn)
    yield prj
    prj.close()


@pytest.fixture
def network_connection(empty_aequilibrae_model):
    with empty_aequilibrae_model.db_connection as conn:
        yield conn


@pytest.fixture
def nauru_no_pop(folder_path):
    shutil.copytree("tests/data/nauru/project", folder_path)
    project = Project()
    project.open(folder_path)

    yield project
    project.close()


@pytest.fixture
def nauru_with_pop(nauru_no_pop, tmp_path):
    shutil.copy(
        os.path.join(os.path.dirname(__file__), "data/nauru/nru--overall--population.tif"),
        os.path.join(tmp_path, "nru--overall--population.tif"),
    )

    population = ImportPopulation(nauru_no_pop)
    population.get_overall_population()

    yield nauru_no_pop
