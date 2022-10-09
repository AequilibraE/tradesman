from os.path import join
from tempfile import gettempdir
import unittest
from uuid import uuid4
from aequilibrae.utils.create_example import create_example
from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.project = create_example(join(gettempdir(), uuid4().hex), "nauru")
        add_new_tables(self.project.conn)
        add_country_borders_to_model("Nauru", self.project)

    def test_load_osm_data_amenity(self):
        tag = "amenity"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]
        self.assertIsNone(load_osm_data(tag="amenity", osm_data={}, queries=query, project=self.project, tile_size=25))

    def test_load_osm_data_building(self):
        tag = "building"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertIsNone(load_osm_data(tag="building", osm_data={}, queries=query, project=self.project, tile_size=25))


if __name__ == "__name__":
    unittest.main()