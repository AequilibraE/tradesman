from shutil import copytree, rmtree
from tempfile import gettempdir
import unittest
from os.path import join, abspath, dirname
from uuid import uuid4
from aequilibrae.project import Project
from tradesman.model_creation.delete_links_and_nodes import delete_links_and_nodes, get_maritime_boundaries


class TestDeleteLinksAndNodes(unittest.TestCase):
    def test_get_maritme_borders(self):

        self.assertIsNone(get_maritime_boundaries("Andorra"))
        self.assertGreater(len(get_maritime_boundaries("Nauru")), 0)
        self.assertGreater(len(get_maritime_boundaries("Brazil")), 0)

    def test_remove_links_and_nodes(self):

        self.temp_fldr = join(gettempdir(), uuid4().hex)

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/vatican city"),
            dst=join(self.temp_fldr, "tests/data/vatican city"),
        )

        self.project = Project()
        self.project.open(join(self.temp_fldr, "tests/data/vatican city"))

        delete_links_and_nodes("Vatican City", self.project)

        num_nodes = len(self.project.conn.execute("SELECT * FROM nodes;").fetchall())
        self.assertEqual(num_nodes, 215)


if __name__ == "__name__":
    unittest.main()
