from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4
import unittest

from aequilibrae.project import Project
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_population import import_population


class TestImportPopulation(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "Nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = Project()
        self.project.new(self.fldr)
        add_new_tables(self.project.conn)
        data = ImportPoliticalSubdivisions(model_place=self.model_place, project=self.project, source="geoBoundaries")
        data.import_model_area()
        data.add_country_borders(overwrite=True)

        self.mock_raster = mock.patch("tradesman.model_creation.import_population.population_raster")
        self.mock_sjoin = mock.patch("tradesman.model_creation.import_population.gpd.sjoin")

        self.mock_raster.start()
        self.mock_sjoin.start()

    def tearDown(self) -> None:
        self.project.close()
        self.mock_raster.stop()
        self.mock_sjoin.stop()

    def test_import_population_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            import_population(project=self.project, model_place=self.model_place, source="OurLand", overwrite=False)

        self.assertEqual(str(exception_context.exception), "No population source found.")

    def test_import_population_meta(self):
        import_population(project=self.project, model_place=self.model_place, source="Meta", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertIsNone(population)

    def test_import_population_meta_exception(self):

        with self.assertRaises(ValueError) as exception_context:
            import_population(project=self.project, model_place="Namibia", source="Meta", overwrite=False)

        self.assertEqual(str(exception_context.exception), "Could not find a population file to import")

    def test_import_population_worldpop(self):
        import_population(project=self.project, model_place=self.model_place, source="WorldPop", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertIsNone(population)


if __name__ == "__name__":
    unittest.main()
