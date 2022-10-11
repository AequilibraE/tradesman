from os.path import join
from tempfile import gettempdir
from uuid import uuid4
import unittest

from aequilibrae.utils.create_example import create_example
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_population import import_population


class TestImportPopulation(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_example(self.fldr, "nauru")
        add_new_tables(self.project.conn)
        ImportPoliticalSubdivisions(self.model_place, self.project, source="GADM").add_country_borders(overwrite=True)

    def tearDown(self) -> None:
        self.project.close()

    def test_import_population_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            import_population(project=self.project, model_place=self.model_place, source="OurLand", overwrite=False)

        self.assertEqual(str(exception_context.exception), "No population source found.")

    def test_import_population_meta(self):
        import_population(project=self.project, model_place=self.model_place, source="Meta", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertGreater(population, 0)

    def test_import_population_meta_exception(self):

        with self.assertRaises(ValueError) as exception_context:
            import_population(project=self.project, model_place="Namibia", source="Meta", overwrite=False)

        self.assertEqual(str(exception_context.exception), "Could not find a population file to import")

    def test_import_population_worldpop(self):
        import_population(project=self.project, model_place=self.model_place, source="WorldPop", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertGreater(population, 0)


if __name__ == "__name__":
    unittest.main()
