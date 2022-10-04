from os.path import join, abspath, dirname
from shutil import copytree
from tempfile import gettempdir
import unittest
from uuid import uuid4
from aequilibrae.utils.create_example import create_example
from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        self.osm_data = {}
        add_new_tables(self.project.conn)
        add_country_borders_to_model("Nauru", self.project)

    # def tearDown(self) -> None:
    #     self.project.close()

    def test_import_osm_data_amenity(self):

        self.assertEqual(
            len(ImportOsmData(tag="amenity", project=self.project, osm_data=self.osm_data).import_osm_data()), 0
        )

    def test_import_osm_data_building(self):

        self.assertEqual(
            len(ImportOsmData(tag="building", project=self.project, osm_data=self.osm_data).import_osm_data()), 0
        )

    def test_import_osm_data_exception(self):

        with self.assertRaises(ValueError) as exception_context:
            ImportOsmData(tag="dinossaur", project=self.project, osm_data=self.osm_data).import_osm_data()

        self.assertEqual(str(exception_context.exception), "Tag value not available.")


if __name__ == "__name__":
    unittest.main()
