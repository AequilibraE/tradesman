from shutil import copytree, rmtree
import unittest
from aequilibrae.project import Project
from os.path import join, abspath, dirname
from tempfile import gettempdir
from uuid import uuid4

from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


class TestSetBoundingBoxes(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        copytree(src=join(abspath(dirname("tests")), "tests/data/vatican city"), dst=self.fldr)
        self.project = Project()
        self.project.open(self.fldr)
        self.osm_data = {}

    def tearDown(self) -> None:
        rmtree(self.fldr, ignore_errors=True)

    def test_set_bounding_boxes(self):
        self.assertEqual(type(bounding_boxes(self.project, km_side=25)), list)


if __name__ == "__name__":
    unittest.main()
