from os import rename
from os.path import join, abspath, dirname
from shutil import copytree, rmtree
from tempfile import gettempdir, mkdtemp
import unittest

from tradesman.model_creation.synthetic_population.syn_pop_validation import validate_non_controlled_vars


class TestValidateNonControlledVars(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "population")
        rename(temp_fldr, self.fldr)

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/output"),
            dst=join(self.fldr, "output"),
        )

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "population"))

    def test_non_controlled_vars(self):
        self.assertEqual(validate_non_controlled_vars("NRU", self.fldr), "Non-controlled vars checked.")


if __name__ == "__name__":
    unittest.main()
