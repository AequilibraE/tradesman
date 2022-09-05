from shutil import rmtree
import unittest
from os.path import join, exists, abspath, dirname
from os import rename
from tempfile import gettempdir, mkdtemp
import requests
from zipfile import ZipFile
from io import BytesIO
from tradesman.model_creation.synthetic_population.seeds_url import population_url
from tradesman.model_creation.synthetic_population.unzip_seed_files import unzip_seed_files


class TestUnzipControlAndSeedFiles(unittest.TestCase):
    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "population"))

    def test_unzip_seed_files_link_exists(self):

        req = requests.get(population_url)

        self.assertTrue(req.status_code == requests.codes.ok)

    def test_unzip_seed_files_early_exit(self):

        temp_fldr = mkdtemp()

        rename(temp_fldr, join(gettempdir(), "population"))

        unzip_seed_files(gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))

    def test_unzip_seed_files_download_files(self):

        zf = ZipFile(BytesIO(abspath(dirname("tests")), "data/nauru/poulation.zip"))

        zf.extractall(gettempdir())

        self.assertTrue(exists(join(gettempdir(), "population")))
