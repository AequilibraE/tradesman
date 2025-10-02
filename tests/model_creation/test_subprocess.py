from os.path import abspath, dirname, exists, join
from shutil import copytree

import pytest

from tradesman.model_creation.synthetic_population.create_synthetic_population import run_populationsim


@pytest.mark.parametrize(("multithread", "num_threads"), [(True, 3), (False, 1)])
def test_subprocess(nauru_no_pop, multithread, num_threads):
    copytree(
        src=join(abspath(dirname("tests")), "tests/data/nauru/population"),
        dst=nauru_no_pop.project_base_path / "population",
    )

    run_populationsim(
        multithread=multithread, project=nauru_no_pop, folder=nauru_no_pop.project_base_path, thread_number=num_threads
    )

    assert exists(join(nauru_no_pop.project_base_path, "population/output/synthetic_households.csv"))

    with nauru_no_pop.db_connection as conn:
        hh_sql = "SELECT COUNT(*) FROM attributes_documentation WHERE name_table='synthetic_households';"
        assert conn.execute(hh_sql).fetchone()[0] == 3

        person_hh = "SELECT COUNT(*) FROM attributes_documentation WHERE name_table='synthetic_persons';"
        assert conn.execute(person_hh).fetchone()[0] == 4
