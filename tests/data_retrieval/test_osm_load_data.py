from os.path import join, abspath, dirname
from shutil import copytree
from tempfile import gettempdir
import unittest
from uuid import uuid4
from aequilibrae.project import Project
from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        copytree(src=join(abspath(dirname("tests")), "data/vatican city"), dst=self.fldr)
        self.project = Project()
        self.project.open(self.fldr)
        self.osm_data = {}

    def test_load_osm_data_amenity(self):
        tag = "amenity"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertIsNone(
            load_osm_data(tag="amenity", osm_data=self.osm_data, queries=query, project=self.project, tile_size=25)
        )

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
