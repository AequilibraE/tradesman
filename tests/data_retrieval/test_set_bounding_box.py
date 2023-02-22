from os.path import join
from tempfile import gettempdir
import unittest
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


class TestSetBoundingBoxes(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)

    def test_set_bounding_boxes(self):
        self.assertEqual(type(bounding_boxes(self.project, km_side=25)), list)


if __name__ == "__name__":
    unittest.main()
