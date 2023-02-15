import unittest
from os.path import abspath, dirname, join
from tempfile import gettempdir
from uuid import uuid4

import pandas as pd
from aequilibrae.utils.create_example import create_example


class TestSaveSyntheticPersons(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        self.pop_fldr = join(abspath(dirname("tests")), "tests/data/nauru/population")

    def test_save_synthetic_persons(self):
        pd.read_csv(join(self.pop_fldr, "output/synthetic_persons.csv")).to_sql(
            "synthetic_persons", con=self.project.conn, if_exists="replace"
        )

        df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", self.project.conn)

        self.assertIn("synthetic_persons", list(df.name))


if __name__ == "__name__":
    unittest.main()
