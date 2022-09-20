from os import remove
from tempfile import gettempdir
from os.path import exists, join, abspath, dirname
from shutil import copy
import unittest

from tradesman.data_retrieval.osm_tags.microsoft_download_file import microsoft_download_file


class TestMicrosoftDownloadFile(unittest.TestCase):
    def setUp(self) -> None:
        copy(
            src=join(abspath(dirname("tests")), "tests/data/vatican city/Vatican City_bing.zip"),
            dst=join(gettempdir(), "Vatican City_bing.zip"),
        )

    def tearDown(self) -> None:
        remove(join(gettempdir(), "Vatican City_bing.zip"))

    def test_microsoft_download_file_url_not_found(self):
        with self.assertRaises(FileNotFoundError) as excepion_context:
            microsoft_download_file("Nauru")

        self.assertEqual(
            str(excepion_context.exception), "Microsoft Bing does not provide information about this region."
        )

    def test_microsoft_download_file_is_file(self):
        microsoft_download_file("Vatican City")
        self.assertTrue(exists(join(gettempdir(), "Vatican City_bing.zip")))


if __name__ == "__name__":
    unittest.main()
