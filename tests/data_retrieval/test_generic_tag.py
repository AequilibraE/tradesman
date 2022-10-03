from os.path import join
from tempfile import gettempdir
import unittest
from unittest.mock import patch
from uuid import uuid4

from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag

# from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data
from tests.create_nauru_test import create_nauru_test


class TestGenericTag(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.osm_data = {
            "amenity": [
                {
                    "type": "node",
                    "id": 1406312122,
                    "lat": -0.5475982,
                    "lon": 166.9175851,
                    "tags": {"amenity": "police", "name": "Police"},
                }
            ]
        }

    @patch("tradesman.data_retrieval.osm_tags.osm_load_data.load_osm_data")
    def test_generic_tag(self, mock_data):

        mock_data.return_value = {
            "amenity": [
                {
                    "type": "node",
                    "id": 1406312122,
                    "lat": -0.5475982,
                    "lon": 166.9175851,
                    "tags": {"amenity": "police", "name": "Police"},
                }
            ]
        }
        self.assertIsNotNone(
            generic_tag(tag="amenity", osm_data=self.osm_data, tile_size=25, project=self.project),
        )


if __name__ == "__name__":
    unittest.main()
