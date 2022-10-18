import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

import pandas as pd
from tests.create_nauru_test import create_nauru_test

from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age


class TestPopBySexAndAge(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)

    def tearDown(self) -> None:
        self.project.close()

    @mock.patch("tradesman.model_creation.pop_by_sex_and_age.load_zones")
    @mock.patch("tradesman.model_creation.pop_by_sex_and_age.population_raster")
    def test_get_pop_by_sex_age(self, mock_raster, mock_zones):
        get_pop_by_sex_age(self.project, self.model_place)

        data = pd.read_sql("SELECT * FROM zones;", con=self.project.conn)

        self.assertIn("POPF10", data.columns)

        self.assertIn("POPF4", data.columns)

        self.assertIn("POPM5", data.columns)

        self.assertIn("POPM7", data.columns)


if __name__ == "__name__":
    unittest.main()
