import unittest
from os.path import join, abspath, dirname
from tempfile import gettempdir
from unittest import mock
from aequilibrae.project import Project
from uuid import uuid4
from shutil import copy, copytree, rmtree
import pandas as pd
from tradesman.data_retrieval.osm_tags.microsoft_building_footage import ImportMicrosoftBuildingData
from aequilibrae.utils.create_example import create_example
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestMicrosoftBuildingFootage(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_initialize(self):
        pass
        
    @unittest.skip
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.ZipFile")
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.isfile")
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.urlretrieve")
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.np.arange")
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.gpd.sjoin")
    # @mock.patch("tradesman.data_retrieval.osm_tags.microsoft_building_footage.gpd.read_file")
    def test_microsoft_buildings(self, patch_gdf, patch_sjoin, patch_url, patch_isfile, patch_zip):

        buildings = ImportMicrosoftBuildingData(model_place="Vatican City", project=self.project)

        buildings.microsoft_buildings()

        df = pd.read_sql("SELECT microsoft_building_count, microsoft_building_area FROM zones;", con=self.project.conn)

        self.assertIn("microsoft_building_count", df.columns.values)


if __name__ == "__name__":
    unittest.main()
