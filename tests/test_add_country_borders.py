import uuid
from os.path import join
from tempfile import gettempdir
import unittest
from tests.create_nauru_test import create_nauru_test


from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.create_new_tables import add_new_tables


class TestCountryBorders(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid.uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.model_place = "Nauru"

    def tearDown(self) -> None:
        self.project.close()

    def test_add_country_borders_to_model_gadm(self):

        add_country_borders_to_model(self.model_place, self.project, source="GADM")

        geo = self.project.conn.execute("SELECT * FROM political_subdivisions WHERE level=0;").fetchall()

        self.assertEqual(len(geo), 1)

    def test_add_country_borders_to_model_geoboundaries(self):

        add_country_borders_to_model(self.model_place, self.project, source="GeoBoundaries")

        geo = self.project.conn.execute("SELECT * FROM political_subdivisions WHERE level=0;").fetchall()

        self.assertEqual(len(geo), 1)


if __name__ == "__name__":
    unittest.main()
