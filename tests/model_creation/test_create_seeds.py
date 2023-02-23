from os.path import join, abspath, dirname
from os import rename
from shutil import copy
from tempfile import gettempdir, mkdtemp
import unittest
from uuid import uuid4
import pandas as pd
from shutil import rmtree
from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.synthetic_population.create_seeds import create_buckets


class TestCreateSeeds(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "data")
        rename(temp_fldr, self.fldr)
        self.project = create_nauru_test(join(gettempdir(), uuid4().hex))

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/seed_households.csv"),
            dst=join(gettempdir(), "data/seed_households.csv"),
        )

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/seed_persons.csv"),
            dst=join(gettempdir(), "data/seed_persons.csv"),
        )

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))

    def test_create_seeds(self):
        create_buckets(self.project, gettempdir())

        x = len(pd.read_csv(join(gettempdir(), "data/seed_households.csv")))

        self.assertGreater(x, 70)


if __name__ == "__name__":
    unittest.main()
