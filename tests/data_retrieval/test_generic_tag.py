import unittest
from unittest import mock

from tradesman.data_retrieval.osm_tags.generic_tag import generic_tag


class TestGenericTag(unittest.TestCase):
    def setUp(self) -> None:
        self.osm_data = {"amenity": "fooboo", "building": "boofoo"}
        self.mock_data = mock.patch("tradesman.data_retrieval.osm_tags.generic_tag.load_osm_data")
        self.mock_prj = mock.patch("tradesman.data_retrieval.osm_tags.generic_tag.Project")
        self.mock_data.start()
        self.mock_prj.start()

    def tearDown(self) -> None:
        self.mock_data.stop()
        self.mock_prj.stop()

    def test_generic_tag_amenity(self):
        self.assertEqual(generic_tag(tag="amenity", project=self.mock_prj, osm_data=self.osm_data), "fooboo")

    def test_generic_tag_building(self):
        self.assertEqual(generic_tag(tag="building", osm_data=self.osm_data, project=self.mock_prj), "boofoo")


if __name__ == "__name__":
    unittest.main()
