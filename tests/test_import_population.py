import unittest
from os.path import join
from tempfile import gettempdir
from unittest import mock
from uuid import uuid4

import pandas as pd
from aequilibrae.project import Project

from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_population import import_population


class TestImportPopulation(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = Project()
        self.project.new(self.fldr)
        add_new_tables(self.project.conn)

    def tearDown(self) -> None:
        self.project.close()

    @mock.patch("tradesman.model_creation.import_population.population_raster")
    def test_import_population_meta(self, mock_raster):

        import_population(project=self.project, model_place="Nauru", source="Meta", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertIsNone(population)

    @mock.patch("tradesman.model_creation.import_population.link_source")
    def test_import_population_meta_exception(self, mock_link):

        mock_link.return_value = "no file"

        with self.assertRaises(ValueError) as exception_context:
            import_population(project=self.project, model_place="Namibia", source="Meta", overwrite=False)

        self.assertEqual(str(exception_context.exception), "Could not find a population file to import")

    @mock.patch("tradesman.model_creation.import_population.link_source")
    @mock.patch("tradesman.model_creation.import_population.population_raster")
    def test_import_population_worldpop(self, mock_raster, mock_link):

        mock_raster.return_value = pd.DataFrame(
            [[166.931666, -0.503333, 7.045551], [166.932499, -0.503333, 5.902642]],
            columns=["longitude", "latitude", "population"],
        )

        import_population(project=self.project, model_place="Nauru", source="WorldPop", overwrite=False)

        population = self.project.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0]

        self.assertGreater(population, 12)


if __name__ == "__name__":
    unittest.main()
