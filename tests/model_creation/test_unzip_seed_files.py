from shutil import rmtree
import unittest
from os.path import join, exists
from os import rename
from tempfile import gettempdir, mkdtemp
from urllib.request import urlopen
from tradesman.model_creation.synthetic_population.seeds_url import population_url
from tradesman.model_creation.synthetic_population.unzip_seed_files import unzip_seed_files


class TestUnzipControlAndSeedFiles(unittest.TestCase):
    def test_unzip_seed_files_link_exists(self):

        self.assertTrue(urlopen(population_url).code == 200)

    def test_unzip_seed_files_early_exit(self):

        rmtree(join(gettempdir(), "population"))

        temp_fldr = mkdtemp()

        rename(temp_fldr, join(gettempdir(), "population"))

        unzip_seed_files(population_url, gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))

    def test_unzip_seed_files_download_files(self):

        unzip_seed_files(population_url, gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))
