from os import remove
from os.path import join, abspath, dirname
from tempfile import gettempdir
import unittest

# from aequilibrae.project import Project
from uuid import uuid4
from shutil import copytree, rmtree
from aequilibrae.utils.create_example import create_example
from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestGenericTag(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        # copytree(src=join(abspath(dirname("tests")), "data/vatican city"), dst=self.fldr)
        self.project = create_example(self.fldr, "nauru")
        self.osm_data = {}
        add_new_tables(self.project.conn)
        add_country_borders_to_model("Nauru", self.project)

    def tearDown(self) -> None:
        rmtree(self.fldr, ignore_errors=True)

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
