import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test

from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.project = create_nauru_test(join(gettempdir(), uuid4().hex))

        self.mock_bbox = mock.patch("tradesman.data_retrieval.osm_tags.osm_load_data.bounding_boxes")
        self.mock_requests = mock.patch("tradesman.data_retrieval.osm_tags.osm_load_data.requests")

        self.mock_bbox.start()
        self.mock_requests.start()

    def tearDown(self) -> None:
        self.project.close()
        self.mock_bbox.stop()
        self.mock_requests.stop()

    def test_load_osm_data_amenity(self):
        tag = "amenity"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertEqual(
            load_osm_data(tag="amenity", osm_data={}, queries=query, project=self.project, tile_size=25),
            {"amenity": []},
        )

    def test_load_osm_data_building(self):
        tag = "building"
        query = [
            f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
            f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        ]

        self.assertEqual(
            load_osm_data(tag="building", osm_data={}, queries=query, project=self.project, tile_size=25),
            {"building": []},
        )


if __name__ == "__name__":
    unittest.main()
