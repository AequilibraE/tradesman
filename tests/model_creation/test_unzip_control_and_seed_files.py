from shutil import rmtree
import unittest
from os.path import join, exists
from os import rename
from tempfile import gettempdir, mkdtemp
from tradesman.model_creation.synthetic_population.unzip_files import unzip_control_and_seed_files


class TestUnzipControlAndSeedFiles(unittest.TestCase):
    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "population"))

    def test_unzip_control_and_seed_files_import(self):

        unzip_control_and_seed_files(gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))

    def test_unzip_control_and_seed_files_early_exit(self):

        temp_fldr = mkdtemp()

        rename(temp_fldr, join(gettempdir(), "population"))

        unzip_control_and_seed_files(gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))
