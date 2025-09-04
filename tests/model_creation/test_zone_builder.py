import pytest

from tradesman.model_creation.build_zoning import ZoneBuilder


@pytest.mark.skip("Still need to fix conftest")
@pytest.mark.parametrize("save_bins", [True, False])
def test_zone_builder(save_bins: bool, nauru_pop_test):
    zones = ZoneBuilder(nauru_pop_test, save_hexbins=save_bins)
    zones.execute()

    with nauru_pop_test.db_connection as conn:
        if save_bins:
            assert conn.execute("SELECT COUNT(*) FROM hex_pop;").fetchone()[0] > 0

        assert conn.execute("SELECT COUNT(*) FROM zones;").fetchone()[0] > 10
