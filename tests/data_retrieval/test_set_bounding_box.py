import unittest
from unittest import mock

from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


class TestSetBoundingBoxes(unittest.TestCase):
    @mock.patch("tradesman.data_retrieval.osm_tags.set_bounding_boxes.gpd.GeoDataFrame.from_postgis")
    @mock.patch("tradesman.data_retrieval.osm_tags.set_bounding_boxes.Project")
    def test_set_bounding_boxes(self, mock_prj, mock_postgis):
        self.assertEqual(type(bounding_boxes(mock_prj, km_side=25)), list)


if __name__ == "__name__":
    unittest.main()
