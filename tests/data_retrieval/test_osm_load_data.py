from os.path import join
from tempfile import gettempdir
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import requests

from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data
import tradesman.data_retrieval.osm_tags.set_bounding_boxes
from tests.create_nauru_test import create_nauru_test


class TestLoadOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        # self.osm_data = {"amenity": []}
        self.queries = [
            '[out:json][timeout:180];(node["amenity"]["area"!~"yes"]({});>;);out geom;',
            '[out:json][timeout:180];(way["amenity"]["area"!~"yes"]({});>;);out geom;',
        ]

    @patch.object(requests, "post")
    @patch.object(tradesman.data_retrieval.osm_tags.set_bounding_boxes, "bounding_boxes")
    def test_load_osm_data(self, mock_box, mock_requests):

        mock_bbox = Mock(return_value=[[42.4288238, 1.4135781, 42.54237975, 1.5999809]])

        mock_box.return_value = mock_bbox

        mock_response = Mock(status_code=200)
        mock_response.json.return_values = {
            "element": [
                {
                    "type": "node",
                    "id": 321679777,
                    "lat": 42.4353428,
                    "lon": 1.5207202,
                    "tags": {
                        "amenity": "restaurant",
                        "name": "la Rabassa",
                        "piste:type": "nordic",
                        "sport": "skiing",
                        "wikidata": "Q3212119",
                    },
                }
            ]
        }

        mock_requests.return_values = mock_response

        self.assertIsNone(
            load_osm_data(tag="amenity", osm_data={}, tile_size=25, queries=self.queries, project=self.project),
        )


if __name__ == "__name__":
    unittest.main()
