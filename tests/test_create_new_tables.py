import uuid
from os.path import join
from tempfile import gettempdir
from unittest import TestCase
from aequilibrae.utils.create_example import create_example
import pandas as pd

from tradesman.model_creation.create_new_tables import add_new_tables


class Test(TestCase):
    def test_add_new_tables(self):
        test_model = create_example(join(gettempdir(), uuid.uuid4().hex))

        add_new_tables(test_model.conn)

        df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", test_model.conn)

        for i in ["political_subdivisions", "raw_population", "hex_pop"]:
            self.assertIn(i, list(df.name))
