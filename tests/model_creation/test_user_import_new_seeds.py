import unittest
from os import rename
from os.path import abspath, dirname, exists, join
from shutil import copy, rmtree
from tempfile import gettempdir, mkdtemp

from tradesman.model_creation.synthetic_population.user_control_import import user_import_new_seeds


class TestUserImportNewSeeds(unittest.TestCase):
    def setUp(self) -> None:
        temp_src = mkdtemp(dir=gettempdir())
        self.src = join(gettempdir(), "data")
        rename(temp_src, self.src)

        temp_dest = mkdtemp(dir=gettempdir())
        self.dest = join(gettempdir(), "destination")
        rename(temp_dest, self.dest)

        data_fldr = mkdtemp(dir=self.dest)
        rename(data_fldr, join(self.dest, "data"))

        copy(src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/seed_persons.csv"), dst=self.src)

        copy(src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/seed_households.csv"), dst=self.src)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))
        rmtree(join(gettempdir(), "destination"))

    def test_user_import_new_seeds_false(self):
        user_import_new_seeds(
            overwrite=False,
            persons_seed_path=join(self.src, "seed_persons.csv"),
            household_seed_path=join(self.src, "seed_households.csv"),
            dest_folder=self.dest,
        )

        self.assertFalse(exists(join(self.dest, "data/seed_persons.csv")))
        self.assertTrue(exists(join(self.src, "seed_persons.csv")))
        self.assertFalse(exists(join(self.dest, "data/seed_households.csv")))
        self.assertTrue(exists(join(self.src, "seed_households.csv")))

    def test_user_import_new_seeds_true(self):
        user_import_new_seeds(
            overwrite=True,
            persons_seed_path=join(self.src, "seed_persons.csv"),
            household_seed_path=join(self.src, "seed_households.csv"),
            dest_folder=self.dest,
        )

        self.assertTrue(exists(join(self.dest, "data/seed_persons.csv")))
        self.assertFalse(exists(join(self.src, "seed_persons.csv")))
        self.assertTrue(exists(join(self.dest, "data/seed_households.csv")))
        self.assertFalse(exists(join(self.src, "seed_households.csv")))


if __name__ == "__name__":
    unittest.main()
