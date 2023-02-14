import unittest
from shutil import rmtree
from os.path import join, exists
from os import rename
from tempfile import gettempdir
import tempfile
from uuid import uuid4
from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk


class TestCreateGeoCrossWalk(unittest.TestCase):
    def setUp(self) -> None:
        self.prj_fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.prj_fldr)
        temp_fldr = tempfile.mkdtemp()
        self.fldr = join(gettempdir(), "data")
        rename(temp_fldr, self.fldr)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))

    def test_create_geo_cross_walk(self):
        create_geo_cross_walk(self.project, gettempdir())

        self.assertTrue(exists(join(gettempdir(), "data/geo_cross_walk.csv")))


if __name__ == "__name__":
    unittest.main()
