import unittest
from os.path import join, abspath, dirname, exists
from tempfile import gettempdir
from aequilibrae.project import Project
from uuid import uuid4
from shutil import copytree, rmtree
import pandas as pd
from tradesman.data_retrieval.osm_tags.microsoft_building_footage import ImportMicrosoftBuildingData


class TestMicrosoftBuildingFootage(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        copytree(src=join(abspath(dirname("tests")), "tests/data/vatican city"), dst=self.fldr)
        self.project = Project()
        self.project.open(self.fldr)
        self.osm_data = {}

    def tearDown(self) -> None:
        rmtree(self.fldr, ignore_errors=True)

    # @unittest.skip
    def test_microsoft_buildings(self):

        ImportMicrosoftBuildingData(model_place="Vatican City", project=self.project).microsoft_buildings()

        df = pd.read_sql("SELECT microsoft_building_count, microsoft_building_area FROM zones", con=self.project.conn)

        self.assertEqual(len(df), 1)

    # @unittest.skip
    def test_initialize(self):
        with self.assertRaises(FileNotFoundError) as exception_context:
            ImportMicrosoftBuildingData(model_place="Papua New Guinea", project=self.project).microsoft_buildings()

        self.assertEqual(
            str(exception_context.exception), "Microsoft Bing does not provide information about this region."
        )


if __name__ == "__name__":
    unittest.main()
