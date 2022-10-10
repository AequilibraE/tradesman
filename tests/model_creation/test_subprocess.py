import unittest
from tempfile import mkdtemp, gettempdir
from os.path import join, abspath, dirname, exists
from os import rename
from shutil import copy, copytree, rmtree
import subprocess
import sys


class TestSubprocess(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "population")
        rename(temp_fldr, self.fldr)

        temp_output = mkdtemp(dir=self.fldr)
        rename(temp_output, join(self.fldr, "output"))

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/run_populationsim.py"),
            dst=join(gettempdir(), "population/run_populationsim.py"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data"),
            dst=join(gettempdir(), "population/data"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/configs"),
            dst=join(gettempdir(), "population/configs"),
        )

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "population"))

    @unittest.skip
    def test_subprocess(self):

        subprocess.run(
            [sys.executable, "run_populationsim.py"],
            cwd=self.fldr,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        self.assertTrue(exists(join(self.fldr, "output/synthetic_households.csv")))


if __name__ == "__name__":
    unittest.main()
