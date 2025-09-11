from os import environ

import pytest

from tradesman.model import Tradesman


@pytest.mark.skipif(bool(environ.get("CI")), reason="Does not run in GitHub Action")
def test_create_model(folder_path):
    proj = Tradesman(folder_path, model_place="San Marino")
    proj.create()

    with proj.project.db_connection as conn:
        assert conn.execute("SELECT COUNT(*) FROM political_subdivisions;").fetchone()[0] > 0
        assert conn.execute("SELECT SUM(population) FROM zones;").fetchone()[0] > 1000
        assert conn.execute("SELECT SUM(f_pop_60) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(m_pop_80) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT COUNT(zone_id) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(ovm_poi_count) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(ovm_bld_area) FROM zones;").fetchone()[0] > 100_000
