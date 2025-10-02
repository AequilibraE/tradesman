import pytest
from unittest import mock

from tradesman.model_creation.import_population import ImportPopulation


class TestPopBySexAndAge:
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            mock.patch("tradesman.model_creation.import_population.ImportPopulation.population_raster"),
            mock.patch("tradesman.model_creation.import_population.gpd.sjoin"),
        ):
            yield

    def test_get_pop_by_sex_age(self, nauru_no_pop):
        population = ImportPopulation(nauru_no_pop)
        population.get_stratified_population()

        with nauru_no_pop.db_connection as conn:
            f_10_pop = conn.execute("SELECT SUM(f_pop_10) FROM zones;").fetchone()[0]
            assert f_10_pop == 0

            f_4_pop = conn.execute("SELECT SUM(f_pop_40) FROM zones;").fetchone()[0]
            assert f_4_pop == 0

            m_5_pop = conn.execute("SELECT SUM(m_pop_5) FROM zones;").fetchone()[0]
            assert m_5_pop == 0

            m_7_pop = conn.execute("SELECT SUM(m_pop_70) FROM zones;").fetchone()[0]
            assert m_7_pop == 0
