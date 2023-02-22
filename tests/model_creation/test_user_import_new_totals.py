import unittest
from os import rename
from os.path import abspath, dirname, exists, join
from shutil import copy, rmtree
from tempfile import gettempdir, mkdtemp

from tradesman.model_creation.synthetic_population.user_control_import import user_import_new_totals


class TestUserImportNewTotals(unittest.TestCase):
    def setUp(self) -> None:
        temp_src = mkdtemp(dir=gettempdir())
        self.src = join(gettempdir(), "data")
        rename(temp_src, self.src)

        temp_dest = mkdtemp(dir=gettempdir())
        self.dest = join(gettempdir(), "destination")
        rename(temp_dest, self.dest)

        data_fldr = mkdtemp(dir=self.dest)
        rename(data_fldr, join(self.dest, "data"))

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/control_totals_taz.csv"),
            dst=self.src,
        )

        copy(
            src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/control_totals_meta.csv"),
            dst=self.src,
        )

        copy(src=join(abspath(dirname("tests")), "tests/data/nauru/population/data/geo_cross_walk.csv"), dst=self.src)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))
        rmtree(join(gettempdir(), "destination"))

    def test_user_import_new_totals_false(self):
        user_import_new_totals(
            overwrite=False,
            totals_lower_level=join(self.src, "control_totals_taz.csv"),
            totals_upper_level=join(self.src, "control_totals_meta.csv"),
            geographies=join(self.src, "geo_cross_walk.csv"),
            dest_folder=self.dest,
        )

        self.assertFalse(exists(join(self.dest, "data/control_totals_taz.csv")))
        self.assertTrue(exists(join(self.src, "control_totals_taz.csv")))
        self.assertFalse(exists(join(self.dest, "data/seed_households.csv")))
        self.assertTrue(exists(join(self.src, "control_totals_meta.csv")))
        self.assertFalse(exists(join(self.dest, "data/control_totals_meta.csv")))
        self.assertTrue(exists(join(self.src, "geo_cross_walk.csv")))

    def test_user_import_new_totals_true(self):
        user_import_new_totals(
            overwrite=True,
            totals_lower_level=join(self.src, "control_totals_taz.csv"),
            totals_upper_level=join(self.src, "control_totals_meta.csv"),
            geographies=join(self.src, "geo_cross_walk.csv"),
            dest_folder=self.dest,
        )

        self.assertTrue(exists(join(self.dest, "data/control_totals_taz.csv")))
        self.assertFalse(exists(join(self.src, "control_totals_taz.csv")))
        self.assertTrue(exists(join(self.dest, "data/control_totals_meta.csv")))
        self.assertFalse(exists(join(self.src, "control_totals_meta.csv")))
        self.assertTrue(exists(join(self.dest, "data/geo_cross_walk.csv")))
        self.assertFalse(exists(join(self.src, "geo_cross_walk.csv")))


if __name__ == "__name__":
    unittest.main()
