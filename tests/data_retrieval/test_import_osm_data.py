from os.path import join, abspath, dirname
from shutil import copytree
from tempfile import gettempdir
import unittest
from uuid import uuid4
from aequilibrae.project import Project
from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        copytree(src=join(abspath(dirname("tests")), "tests/data/vatican city"), dst=self.fldr)
        self.project = Project()
        self.project.open(self.fldr)
        self.osm_data = {}

    def tearDown(self) -> None:
        self.project.close()

    def test_import_osm_data_amenity(self):

        self.assertGreater(
            len(ImportOsmData(tag="amenity", project=self.project, osm_data=self.osm_data).import_osm_data()), 0
        )

    def test_import_osm_data_building(self):

        self.assertGreater(
            len(ImportOsmData(tag="building", project=self.project, osm_data=self.osm_data).import_osm_data()), 0
        )

    def test_import_osm_data_exception(self):

        with self.assertRaises(ValueError) as exception_context:
            ImportOsmData(tag="dinossaur", project=self.project, osm_data=self.osm_data).import_osm_data()

        self.assertEqual(str(exception_context.exception), "Tag value not available.")


if __name__ == "__name__":
    unittest.main()
