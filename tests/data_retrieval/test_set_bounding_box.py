import unittest
from os.path import join
from tempfile import gettempdir
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.utils import set_bbox


class TestSetBoundingBoxes(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)

    def test_set_bounding_boxes(self):
        xmin = float(self.project.about.xmin)
        xmax = float(self.project.about.xmax)
        ymin = float(self.project.about.ymin)
        ymax = float(self.project.about.ymax)

        self.assertEqual(type(set_bbox(xmin, ymin, xmax, ymax, box_side=25)), list)


if __name__ == "__name__":
    unittest.main()
