from os import remove
from shutil import copy
import unittest
from os.path import join, abspath, dirname
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4
import pandas as pd
# from aequilibrae.utils.create_example import create_example
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.create_new_tables import add_new_tables
from aequilibrae.project import Project


class TestImportPoliticalSubvisions(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = Project()
        self.project.new(self.fldr)
        add_new_tables(self.project.conn)

        copy(src=join(abspath(dirname("tests")), "tests/data/nauru/gadm_NRU.gpkg"), dst=join(gettempdir(), "gadm_NRU.gpkg"))

        self.gadm_data = ImportPoliticalSubdivisions(model_place=self.model_place, source="gadm", project=self.project)
        self.geob_data = ImportPoliticalSubdivisions(model_place=self.model_place, source="geoboundaries", project=self.project)

    def tearDown(self) -> None:
        self.project.close()

    def test_import_model_area_exception(self):
        data = ImportPoliticalSubdivisions(model_place="Charlie and the Chocolate Factory", source="gadm", project=self.project)

        with self.assertRaises(ValueError) as exception_context:
            data.import_model_area()
        
        self.assertEqual(str(exception_context.exception), "The desired model place is not available.")

    def test_source_control_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            ImportPoliticalSubdivisions(model_place=self.model_place, source="dinossaur", project=self.project)

        self.assertEqual(str(exception_context.exception), "Source not available.")

    @mock.patch("tradesman.model_creation.import_political_subdivisions.urlretrieve")
    def test_add_country_borders_gadm(self, mock_request):
        self.gadm_data.import_model_area()
        self.gadm_data.add_country_borders(overwrite=False)
        self.gadm_data.import_subdivisions(level=2, overwrite=False)

        self.assertEqual(self.gadm_data.country_name, "Nauru")
        self.assertEqual(self.gadm_data.model_place, "Nauru")
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=-1;", con=self.project.conn)), 1
        )
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=0;", con=self.project.conn)), 1
        )
        self.assertGreater(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level>0;", con=self.project.conn)), 1
        )

        remove(join(gettempdir(), "nru_cache_gadm.parquet"))

    def test_add_country_borders_geoboundaries(self):

        self.geob_data.import_model_area()
        self.geob_data.add_country_borders(overwrite=False)
        self.geob_data.import_subdivisions(level=2, overwrite=False)

        self.assertEqual(self.geob_data.country_name, "Nauru")
        self.assertEqual(self.geob_data.model_place, "Nauru")
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=-1;", con=self.project.conn)), 1
        )
        self.assertEqual(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level=0;", con=self.project.conn)), 1
        )
        self.assertGreater(
            len(pd.read_sql("SELECT * FROM political_subdivisions WHERE level>0;", con=self.project.conn)), 1
        )

        remove(join(gettempdir(), "nru_cache_geoboundaries.parquet"))


if __name__ == "__name__":
    unittest.main()
