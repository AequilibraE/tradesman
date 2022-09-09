from tempfile import gettempdir
import unittest
from uuid import uuid4
from os.path import join
from aequilibrae.utils.create_example import create_example

from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.get_political_subdivision import (
    add_subdivisions_to_model,
    get_subdivisions_gadm,
    get_subdivisions_online,
)


class TestImportSubdivision(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.project = create_example(join(gettempdir(), uuid4().hex), "nauru")
        add_new_tables(self.project.conn)

    def tearDown(self) -> None:
        return super().tearDown()

    @unittest.skip
    def test_import_subdivision_gadm(self):
        self.assertGreater(len(get_subdivisions_gadm(self.model_place, level=1)), 0)

    def test_import_subdivision_geoboundaries(self):

        self.assertGreater(len(get_subdivisions_online(self.model_place, level=1)), 0)

    @unittest.skip
    def test_add_subdivisions_to_model_gadm(self):
        add_subdivisions_to_model(self.project, self.model_place, source="GADM", levels_to_add=1, overwrite=False)

        self.assertGreater(
            len(self.project.conn.execute("SELECT * FROM political_subdivisions WHERE level>0;").fetchall()), 0
        )

    def test_add_subdivisions_to_model_geoboundaries(self):

        add_subdivisions_to_model(
            self.project, self.model_place, source="geoboundaries", levels_to_add=1, overwrite=False
        )

        self.assertGreater(
            len(self.project.conn.execute("SELECT * FROM political_subdivisions WHERE level>0;").fetchall()), 0
        )

    def test_add_subdivisions_to_model_error(self):
        with self.assertRaises(ValueError) as exception_context:
            add_subdivisions_to_model(
                self.project, self.model_place, source="OurLand", levels_to_add=1, overwrite=False
            )

        self.assertEqual(str(exception_context.exception), "This subdivision source is not available.")


if __name__ == "__name__":
    unittest.main()
