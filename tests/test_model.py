import os
import unittest
import uuid
from os.path import join
from tempfile import gettempdir

from tradesman.model import Tradesman


class TestModel(unittest.TestCase):
    def setUp(self) -> None:
        dir = join(gettempdir(), uuid.uuid4().hex)
        self.proj = Tradesman(dir, "San Marino")

    @unittest.skipIf(os.environ.get("CI", "false") == "true", "Running on GitHub")
    def test_create(self):
        self.proj.create()

        self.assertGreater(
            self.proj._project.conn.execute("SELECT COUNT(*) FROM political_subdivisions;").fetchone()[0], 0
        )
        self.assertGreater(self.proj._project.conn.execute("SELECT SUM(population) FROM zones;").fetchone()[0], 1000)
        self.assertGreater(self.proj._project.conn.execute("SELECT SUM(POPF13) FROM zones;").fetchone()[0], 10)
        self.assertGreater(self.proj._project.conn.execute("SELECT SUM(POPM18) FROM zones;").fetchone()[0], 10)
        self.assertEqual(self.proj._project.conn.execute("SELECT COUNT(zone_id) FROM zones;").fetchone()[0], 8)
        self.assertGreater(
            self.proj._project.conn.execute("SELECT SUM(osm_amenity_count) FROM zones;").fetchone()[0], 10
        )
        self.assertGreater(
            self.proj._project.conn.execute("SELECT SUM(microsoft_building_count) FROM zones;").fetchone()[0], 10
        )
        self.assertGreater(
            self.proj._project.conn.execute("SELECT SUM(osm_building_area) FROM zones;").fetchone()[0], 100_000
        )

    # def test_set_population_source(self):
    #     self.fail()

    # def test_import_network(self):
    #     self.proj.import_network()

    # def test_import_subdivisions(self):
    #     self.fail()
    #
    # def test_import_population(self):
    #     self.fail()
    #
    # def test_build_zoning(self):
    #     self.proj.build_zoning(overwrite=True)
    #

    # def test_place(self):
    #     self.fail()
