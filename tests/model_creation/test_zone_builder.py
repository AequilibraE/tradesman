import pytest

from tradesman.model_creation.build_zoning import ZoneBuilder


@pytest.mark.parametrize("save_bins", [True, False])
def test_zone_builder(save_bins: bool, nauru_with_pop):
    with nauru_with_pop.db_connection as conn:
        conn.execute("DELETE FROM zones;")

    zones = ZoneBuilder(nauru_with_pop, max_zone_pop=1_000, min_zone_pop=200, save_hexbins=save_bins)
    zones.execute()

    with nauru_with_pop.db_connection as conn:
        if save_bins:
            assert conn.execute("SELECT COUNT(*) FROM hex_pop;").fetchone()[0] > 0

        assert conn.execute("SELECT COUNT(*) FROM zones;").fetchone()[0] > 10
