from os.path import join, abspath, dirname
from tempfile import gettempdir
import unittest
from aequilibrae.project import Project
from uuid import uuid4
from shutil import copytree
from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag


class TestGenericTag(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        copytree(src=join(abspath(dirname("tests")), "tests/data/vatican city"), dst=self.fldr)
        self.project = Project()
        self.project.open(self.fldr)
        self.osm_data = {}

    def tearDown(self) -> None:
        self.project.close()

    def test_generic_tag_amenity(self):

        self.assertEqual(
            type(generic_tag(tag="amenity", osm_data=self.osm_data, tile_size=25, project=self.project)), list
        )

    def test_generic_tag_building(self):

        self.assertEqual(
            type(generic_tag(tag="building", osm_data=self.osm_data, tile_size=25, project=self.project)), list
        )


if __name__ == "__name__":
    unittest.main()
