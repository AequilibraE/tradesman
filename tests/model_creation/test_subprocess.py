import unittest
from tempfile import gettempdir
from os.path import join, abspath, dirname, exists
from shutil import copytree, rmtree
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.synthetic_population.create_synthetic_population import run_populationsim


class TestSubprocess(unittest.TestCase):
    def setUp(self) -> None:
        self.project_folder = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.project_folder)

        self.fldr = join(self.project_folder, "population")

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population"),
            dst=self.fldr,
        )

    def tearDown(self) -> None:
        rmtree(self.fldr)

    def test_subprocess(self):
        run_populationsim(multithread=False, project=self.project, folder=self.project_folder, thread_number=1)

        self.__dochecks()

    def test_subprocess_true(self):
        run_populationsim(multithread=True, project=self.project, folder=self.project_folder, thread_number=3)
        self.__dochecks()

    def __dochecks(self):
        self.assertTrue(exists(join(self.fldr, "output/synthetic_households.csv")))

        hh_sql = "SELECT COUNT(*) FROM attributes_documentation WHERE name_table='synthetic_households';"
        self.assertEqual(self.project.conn.execute(hh_sql).fetchone()[0], 3)

        person_hh = "SELECT COUNT(*) FROM attributes_documentation WHERE name_table='synthetic_persons';"
        self.assertEqual(self.project.conn.execute(person_hh).fetchone()[0], 4)


if __name__ == "__name__":
    unittest.main()
