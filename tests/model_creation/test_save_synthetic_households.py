import unittest
import pandas as pd
from os.path import join, abspath, dirname
from tempfile import gettempdir
from uuid import uuid4

from aequilibrae.utils.create_example import create_example


class TestSaveSyntheticHouseholds(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        self.pop_fldr = join(abspath(dirname("tests")), "tests/data/nauru/population")

    def test_save_synthetic_households(self):
        pd.read_csv(join(self.pop_fldr, "output/synthetic_households.csv")).to_sql(
            "synthetic_households", con=self.project.conn, if_exists="replace"
        )

        df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", self.project.conn)

        self.assertIn("synthetic_households", list(df.name))


if __name__ == "__name__":
    unittest.main()
