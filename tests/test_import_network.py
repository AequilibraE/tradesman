from os.path import join, abspath, dirname
from tempfile import gettempdir
import requests
import unittest
from unittest import mock
from uuid import uuid4
from aequilibrae import Project, Parameters

import pandas as pd

from tradesman.model_creation.import_network import ImportNetwork


class TestImportNetwork(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)

        self.project = Project()
        self.project.new(self.fldr)

        self.pbf_path = join(abspath(dirname("tests")), "tests/data/monaco/monaco-latest.osm.pbf")
        self.model_place = "Monaco"

        try:
            requests.get("https://lz4.overpass-api.de/api/interpreter")
        except requests.exceptions.ConnectionError:
            par = Parameters()
            par.parameters["osm"]["overpass_endpoint"] = "https://overpass.kumi.systems/api/interpreter"
            par.write_back()

    def tearDown(self) -> None:
        self.project.close()

    def test_import_from_osm(self):
        network = ImportNetwork(self.project, self.model_place)
        network.build_network()

        links = pd.read_sql("SELECT * FROM links;", con=self.project.conn)

        self.assertGreater(len(links), 0)
        self.assertIn("bridge", links.columns)
        self.assertIn("toll", links.columns)
        self.assertIn("tunnel", links.columns)

    @mock.patch("tradesman.model_creation.import_network.bounding_boxes")
    def test_import_from_gmns(self, patch_box):
        network = ImportNetwork(self.project, self.model_place, self.pbf_path)
        network.build_network()

        links = pd.read_sql("SELECT * FROM links;", con=self.project.conn)

        self.assertGreater(len(links), 0)
        self.assertIn("bridge", links.columns)
        self.assertIn("toll", links.columns)
        self.assertIn("tunnel", links.columns)


if __name__ == "__name__":
    unittest.main()
