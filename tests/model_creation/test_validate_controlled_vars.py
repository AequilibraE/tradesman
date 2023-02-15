import unittest
from tempfile import mkdtemp, gettempdir
from os.path import join, abspath, dirname, exists
from os import rename
from shutil import copy, copytree, rmtree

from tradesman.model_creation.synthetic_population.syn_pop_validation import validate_controlled_vars
from tradesman.model_creation.synthetic_population.user_control_import import user_change_validation_parameters


class TestValidateControlledVars(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "population")
        rename(temp_fldr, self.fldr)

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/verification.yaml"),
            dst=self.fldr,
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/output"),
            dst=join(self.fldr, "output"),
        )

        copytree(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data"),
            dst=join(self.fldr, "data"),
        )

        user_change_validation_parameters(overwrite=False, model_place="Nauru", dest_folder=self.fldr)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "population"))

    def test_validate_controlled_vars(self):
        validate_controlled_vars(self.fldr)

        self.assertTrue(exists(join(self.fldr, "validation_results")))


if __name__ == "__name__":
    unittest.main()
