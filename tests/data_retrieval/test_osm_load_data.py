from os.path import join, abspath, dirname
from shutil import copytree, rmtree
from tempfile import gettempdir
import unittest
from uuid import uuid4
from aequilibrae.utils.create_example import create_example
from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        self.osm_data = {}
        add_new_tables(self.project.conn)
        add_country_borders_to_model("Nauru", self.project)

    def tearDown(self) -> None:
        rmtree(self.fldr, ignore_errors=True)

    @unittest.skip
    def test_load_osm_data_amenity(self):
        tag = "amenity"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertIsNone(
            load_osm_data(tag="amenity", osm_data=self.osm_data, queries=query, project=self.project, tile_size=25)
        )

    @unittest.skip
    def test_load_osm_data_building(self):
        tag = "building"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertIsNone(
            load_osm_data(tag="building", osm_data=self.osm_data, queries=query, project=self.project, tile_size=25)
        )


if __name__ == "__name__":
    unittest.main()
