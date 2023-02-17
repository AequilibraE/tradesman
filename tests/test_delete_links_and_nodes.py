import unittest
from os.path import abspath, dirname, join
from shutil import copytree
from tempfile import gettempdir
from uuid import uuid4
import fiona
from aequilibrae.project import Project

from tradesman.model_creation.delete_links_and_nodes import (
    delete_links_and_nodes,
    get_maritime_boundaries,
    place_is_country,
)


class TestDeleteLinksAndNodes(unittest.TestCase):
    def test_get_maritme_borders(self):
        self.assertIsNone(get_maritime_boundaries("Andorra"))
        self.assertGreater(len(get_maritime_boundaries("Nauru")), 0)
        self.assertGreater(len(get_maritime_boundaries("Brazil")), 0)

    def test_is_country(self):
        self.assertTrue(place_is_country("Andorra"))
        self.assertTrue(place_is_country("Nauru"))
        self.assertTrue(place_is_country("Brazil"))
        self.assertFalse(place_is_country("Vorarlberg"))
        self.assertFalse(place_is_country("Minas Gerais"))

    def test_remove_links_and_nodes_no_maritime(self):
        self.temp_fldr = join(gettempdir(), uuid4().hex)

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/vatican city/project"),
            dst=join(self.temp_fldr, "tests/data/vatican city"),
        )

        self.project = Project()
        self.project.open(join(self.temp_fldr, "tests/data/vatican city"))

        before = len(self.project.conn.execute("SELECT * FROM nodes;").fetchall())

        delete_links_and_nodes("Vatican City", self.project)

        num_nodes = len(self.project.conn.execute("SELECT * FROM nodes;").fetchall())

        self.assertGreater(before, num_nodes)

    def test_remove_links_and_nodes_maritime(self):
        self.temp_fldr = join(gettempdir(), uuid4().hex)

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/monaco/project"),
            dst=join(self.temp_fldr, "tests/data/monaco"),
        )

        self.project = Project()
        self.project.open(join(self.temp_fldr, "tests/data/monaco"))

        before = len(self.project.conn.execute("SELECT * FROM nodes;").fetchall())

        delete_links_and_nodes("Monaco", self.project)

        num_nodes = len(self.project.conn.execute("SELECT * FROM nodes;").fetchall())

        self.assertGreater(before, num_nodes)


if __name__ == "__name__":
    unittest.main()
