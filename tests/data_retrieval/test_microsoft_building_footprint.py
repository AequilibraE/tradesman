import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

import pandas as pd

from tests.create_nauru_test import create_nauru_test
from tradesman.data_retrieval.osm_tags.microsoft_building_footprint import ImportMicrosoftBuildingData


class TestMicrosoftBuildingFootprint(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)

    def test_initialize(self):
        png = ImportMicrosoftBuildingData(model_place="Papua New Guinea", project=self.project)
        self.assertFalse(png._available, "Should not have for PNG")

        brl = ImportMicrosoftBuildingData(model_place="Brazil", project=self.project)
        self.assertTrue(brl._available, "Should have for Brazil")

    # @unittest.skip
    @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footprint.max")
    def test_microsoft_buildings(self, mock_max):
        buildings = ImportMicrosoftBuildingData(model_place="Vatican City", project=self.project)

        buildings.microsoft_buildings()

        df = pd.read_sql("SELECT microsoft_building_count, microsoft_building_area FROM zones;", con=self.project.conn)

        self.assertIn("microsoft_building_count", df.columns.values)


if __name__ == "__name__":
    unittest.main()
