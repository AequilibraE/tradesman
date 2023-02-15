import unittest
from shutil import copy
from os.path import join, exists, abspath, dirname
from os import rename
from tempfile import gettempdir, mkdtemp
from shutil import rmtree

from tradesman.model_creation.synthetic_population.create_control_totals_meta import create_control_totals_meta


class TestCreateTotalsMeta(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "data")
        rename(temp_fldr, self.fldr)

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/control_totals_taz.csv"),
            dst=join(gettempdir(), "data/control_totals_taz.csv"),
        )

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))

    def test_create_totals_meta(self):
        create_control_totals_meta(gettempdir())

        self.assertTrue(exists(join(gettempdir(), "data/control_totals_meta.csv")))


if __name__ == "__name__":
    unittest.main()
