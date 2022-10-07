# from os import remove
from os.path import join
from tempfile import gettempdir
import unittest
from unittest import mock
from uuid import uuid4
from shutil import rmtree

from aequilibrae.utils.create_example import create_example
from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag

from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestGenericTag(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        # copytree(src=join(abspath(dirname("tests")), "data/vatican city/project"), dst=self.fldr)
        self.project = create_example(self.fldr, "nauru")
        add_new_tables(self.project.conn)
        add_country_borders_to_model("Nauru", self.project)
        self.osm_data = {"amenity": "fooboo", "building": "boofoo"}
        self.patcher = mock.patch("tradesman.data_retrieval.osm_tags.generic_tag.load_osm_data")
        self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()
        rmtree(self.fldr, ignore_errors=True)

    def test_generic_tag_amenity(self):
        self.assertEqual(generic_tag(tag="amenity", project=self.project, osm_data=self.osm_data), "fooboo")

    def test_generic_tag_building(self):

        self.assertEqual(generic_tag(tag="building", osm_data=self.osm_data, project=self.project), "boofoo")


if __name__ == "__name__":
    unittest.main()
