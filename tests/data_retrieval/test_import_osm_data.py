import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData


class TestImportOsmData(unittest.TestCase):
    def setUp(self) -> None:
        self.project = create_nauru_test(join(gettempdir(), uuid4().hex))
        self.osm_data = {}

    def tearDown(self) -> None:
        self.project.close()

    @mock.patch("tradesman.data_retrieval.osm_tags.import_osm_data.generic_tag")
    def test_import_osm_data_amenity(self, mock_tag):
        mock_tag.return_value = [
            {
                "type": "node",
                "id": 1406312122,
                "lat": -0.5475982,
                "lon": 166.9175851,
                "tags": {"amenity": "police", "name": "Police"},
            }
        ]

        data = ImportOsmData(tag="amenity", project=self.project, osm_data=self.osm_data)

        self.assertEqual(len(data.import_osm_data()), 1)

    @mock.patch("tradesman.data_retrieval.osm_tags.import_osm_data.generic_tag")
    def test_import_osm_data_building(self, mock_tag):
        mock_tag.return_value = [
            {
                "type": "way",
                "id": 107982310,
                "bounds": {"minlat": -0.545025, "minlon": 166.9172539, "maxlat": -0.5444982, "maxlon": 166.91783},
                "nodes": [1239833064, 4237493750, 1726551128, 1726551158, 1239875402, 1239833064],
                "geometry": [
                    {"lat": -0.5446485, "lon": 166.9172539},
                    {"lat": -0.5444982, "lon": 166.9173795},
                    {"lat": -0.5447808, "lon": 166.9177177},
                    {"lat": -0.5448747, "lon": 166.91783},
                    {"lat": -0.545025, "lon": 166.9177044},
                    {"lat": -0.5446485, "lon": 166.9172539},
                ],
                "tags": {"aeroway": "terminal", "building": "transportation", "name": "Nauru Airport Terminal"},
            }
        ]

        data = ImportOsmData(tag="building", project=self.project, osm_data=self.osm_data)

        self.assertEqual(len(data.import_osm_data()), 1)

    def test_import_osm_data_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            ImportOsmData(tag="dinosaur", project=self.project, osm_data=self.osm_data).import_osm_data()

        self.assertEqual(str(exception_context.exception), "Tag value not available.")


if __name__ == "__name__":
    unittest.main()
