from os import remove, rename
from os.path import join, exists, abspath, dirname
from shutil import copy, rmtree
from tempfile import gettempdir, mkdtemp
import unittest
from webbrowser import get

from tradesman.model_creation.synthetic_population.user_control_import import user_change_controls


class TestUserChangeControls(unittest.TestCase):
    def setUp(self) -> None:
        temp_src = mkdtemp()
        self.src = join(gettempdir(), "configs")
        rename(temp_src, self.src)

        temp_dest = mkdtemp()
        self.dest = join(gettempdir(), "destination")
        rename(temp_dest, self.dest)

        config_fldr = mkdtemp(dir=self.dest)
        rename(config_fldr, join(self.dest, "configs"))

        copy(src=join(abspath(dirname("tests")), "tests/data/nauru/population/configs/controls.csv"), dst=self.src)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "configs"))
        rmtree(join(gettempdir(), "destination"))

    def test_user_change_controls_false(self):
        user_change_controls(overwrite=False)

        self.assertTrue(exists(join(self.src, "controls.csv")))
        self.assertFalse(exists(join(self.dest, "configs/controls.csv")))

    def test_user_change_controls_true(self):
        user_change_controls(
            overwrite=True,
            src_file=join(self.src, "controls.csv"),
            dest_folder=self.dest,
        )

        self.assertTrue(exists(join(self.dest, "configs/controls.csv")))
        self.assertFalse(exists(join(self.src, "controls.csv")))


if __name__ == "__name__":
    unittest.main()
