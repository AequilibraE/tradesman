import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age


class TestPopBySexAndAge(unittest.TestCase):
    def setUp(self) -> None:
        self.country_name = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.mock_raster = mock.patch("tradesman.model_creation.pop_by_sex_and_age.population_raster")
        self.mock_sjoin = mock.patch("tradesman.model_creation.pop_by_sex_and_age.gpd.sjoin")

        self.mock_raster.start()
        self.mock_sjoin.start()

    def tearDown(self) -> None:
        self.project.close()
        self.mock_raster.stop()
        self.mock_sjoin.stop()

    def test_get_pop_by_sex_age(self):
        get_pop_by_sex_age(self.project, self.country_name)

        f_10_pop = self.project.conn.execute("SELECT SUM(POPF10) FROM zones;").fetchone()[0]
        self.assertEqual(f_10_pop, 0)

        f_4_pop = self.project.conn.execute("SELECT SUM(POPF4) FROM zones;").fetchone()[0]
        self.assertEqual(f_4_pop, 0)

        m_5_pop = self.project.conn.execute("SELECT SUM(POPM5) FROM zones;").fetchone()[0]
        self.assertEqual(m_5_pop, 0)

        m_7_pop = self.project.conn.execute("SELECT SUM(POPM7) FROM zones;").fetchone()[0]
        self.assertEqual(m_7_pop, 0)


if __name__ == "__name__":
    unittest.main()
