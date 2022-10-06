from os import remove, walk
from re import compile
import unittest
from os.path import join
from tempfile import gettempdir
from uuid import uuid4
import pandas as pd
from aequilibrae.utils.create_example import create_example
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.create_new_tables import add_new_tables


class TestImportPoliticalSubvisions(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        add_new_tables(self.project.conn)
        self.data = ImportPoliticalSubdivisions(model_place="Nauru", project=self.project)

    def test_add_country_borders_gadm(self):

        self.data.add_country_borders(source="gadm", overwrite=True)
        self.data.import_subdivisions(source="gadm", level=2, overwrite=True)

        self.assertEqual(self.data.country_name, "Nauru")
        self.assertEqual(self.data.model_place, "Nauru")
        self.assertGreater(len(pd.read_sql("SELECT * FROM political_subdivisions;", con=self.project.conn)), 1)
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=0;", con=self.project.conn)), 1
        )
        self.assertGreater(len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level>0;", con=self.project.conn)), 2)

        remove(join(gettempdir(), "nru_cache_gadm.parquet"))

    def test_add_country_borders_geoboundaries(self):

        self.data.add_country_borders(source="geoboundaries", overwrite=True)
        self.data.import_subdivisions(source="geoboundaries", level=2, overwrite=True)

        self.assertEqual(self.data.country_name, "Nauru")
        self.assertEqual(self.data.model_place, "Nauru")
        self.assertGreater(len(pd.read_sql("SELECT * FROM political_subdivisions;", con=self.project.conn)), 1)
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=0;", con=self.project.conn)), 1
        )
        self.assertGreater(len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level>0;", con=self.project.conn)), 2)

        remove(join(gettempdir(), "nru_cache_geoboundaries.parquet"))

    def test_get_subdivisons_exception_ab(self):
        self.data.add_country_borders(source="gadm", overwrite=True)

        with self.assertRaises(ValueError) as exception_context:
            self.data.import_subdivisions(source="geoboundaries", level=2, overwrite=True)

        self.assertEqual(
            str(exception_context.exception),
            "Data Source from country_borders is different from political_subdivisions.",
        )

        remove(join(gettempdir(), "nru_cache_gadm.parquet"))

    def test_get_subdivisons_exception_ba(self):
        self.data.add_country_borders(source="geoboundaries", overwrite=True)

        with self.assertRaises(ValueError) as exception_context:
            self.data.import_subdivisions(source="gadm", level=2, overwrite=True)

        self.assertEqual(
            str(exception_context.exception),
            "Data Source from country_borders is different from political_subdivisions.",
        )

        remove(join(gettempdir(), "nru_cache_geoboundaries.parquet"))


if __name__ == "__name__":
    unittest.main()
