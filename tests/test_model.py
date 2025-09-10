from os import environ
import pytest

from tradesman.model import Tradesman


@pytest.mark.skip("Temporary skip running this test")
@pytest.mark.skipif(bool(environ.get("CI")), reason="Does not run in GitHub Action")
def test_create_model(folder_path):
    proj = Tradesman(folder_path, model_place="San Marino")
    proj.create()

    with proj.project.db_connection as conn:
        assert conn.execute("SELECT COUNT(*) FROM political_subdivisions;").fetchone()[0] > 0
        assert conn.execute("SELECT SUM(population) FROM zones;").fetchone()[0] > 1000
        assert conn.execute("SELECT SUM(POPF13) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(POPM18) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT COUNT(zone_id) FROM zones;").fetchone()[0] == 8
        assert conn.execute("SELECT SUM(osm_amenity_count) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(microsoft_building_count) FROM zones;").fetchone()[0] > 10
        assert conn.execute("SELECT SUM(osm_building_area) FROM zones;").fetchone()[0] > 100_000
