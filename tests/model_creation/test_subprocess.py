import unittest
from tempfile import mkdtemp, gettempdir
from os.path import join, abspath, dirname, exists
from os import rename
from shutil import copy, copytree, rmtree
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.synthetic_population.create_synthetic_population import run_populationsim


class TestSubprocess(unittest.TestCase):
    def setUp(self) -> None:
        self.project_folder = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.project_folder)

        self.fldr = join(self.project_folder, "population")
        rename(mkdtemp(dir=self.project_folder), self.fldr)

        temp_output = mkdtemp(dir=self.fldr)
        rename(temp_output, join(self.fldr, "output"))

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/run_populationsim.py"),
            dst=join(self.project_folder, "population/run_populationsim.py"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data"),
            dst=join(self.project_folder, "population/data"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/configs"),
            dst=join(self.project_folder, "population/configs"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/configs_mp"),
            dst=join(self.project_folder, "population/configs_mp"),
        )

    def tearDown(self) -> None:
        rmtree(self.fldr)

    @unittest.skip
    def test_subprocess_false(self):

        run_populationsim(multithread=False, project=self.project, folder=self.project_folder, thread_number=1)

        self.assertTrue(exists(join(self.fldr, "output/synthetic_households.csv")))

        # self.project.close()

    @unittest.skip
    def test_subprocess_true(self):

        run_populationsim(multithread=True, project=self.project, folder=self.project_folder, thread_number=3)

        self.assertTrue(exists(join(self.fldr, "output/synthetic_households.csv")))

        # self.project.close()


if __name__ == "__name__":
    unittest.main()
