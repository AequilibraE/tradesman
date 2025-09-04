from os.path import join, abspath, dirname
from tempfile import gettempdir
import requests
import unittest
from unittest import mock
from uuid import uuid4
from aequilibrae import Project, Parameters
import pytest

import pandas as pd

from tradesman.model_creation.import_network import ImportNetwork


@pytest.mark.skip("Still need to fix this test")
class TestImportNetwork(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)

        self.project = Project()
        self.project.new(self.fldr)

        fields = ["model_place", "address_type", "country_name", "country_code_two_digit", "country_code_three_digit"]
        fields.extend(["xmin", "ymin", "xmax", "ymax"])

        about = self.project.about
        for field in fields:
            about.add_info_field(field)

        about.model_place = "Monaco"
        about.address_type = "country"
        about.country_name = "Monaco"
        about.country_code_two_digit = "MC"
        about.country_code_three_digit = "MCO"
        about.xmin = 7.4037113
        about.ymin = 43.7196129
        about.xmax = 7.4876594
        about.ymax = 43.7574357

        self.pbf_path = join(abspath(dirname("tests")), "tests/data/monaco/monaco-latest.osm.pbf")
        self.model_place = "Monaco"

    def tearDown(self) -> None:
        self.project.close()

    def test_import_from_osm(self):
        network = ImportNetwork(self.project, self.model_place)
        network.build_network()

        with self.project.db_connection as conn:
            links = pd.read_sql("SELECT * FROM links;", con=conn)

        self.assertGreater(len(links), 0)
        self.assertIn("bridge", links.columns)
        self.assertIn("toll", links.columns)
        self.assertIn("tunnel", links.columns)

    @mock.patch("tradesman.utils.set_bbox")
    def test_import_from_gmns(self, patch_box):
        network = ImportNetwork(self.project, self.model_place, self.pbf_path)
        network.build_network()

        with self.project.db_connection as conn:
            links = pd.read_sql("SELECT * FROM links;", con=conn)

        self.assertGreater(len(links), 0)
        self.assertIn("bridge", links.columns)
        self.assertIn("toll", links.columns)
        self.assertIn("tunnel", links.columns)


if __name__ == "__name__":
    unittest.main()
