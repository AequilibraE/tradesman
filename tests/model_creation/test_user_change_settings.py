from os import rename
from os.path import join
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
import yaml
import unittest

from tradesman.model_creation.synthetic_population.user_control_import import user_change_settings


class TestUserChangeSettings(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "configs")
        rename(temp_fldr, self.fldr)

        dct = {"output_synthetic_population": {"persons": {"columns": []}, "households": {"columns": []}}}

        with open(join(self.fldr, "settings.yaml"), mode="w") as file:
            yaml.dump(dct, file, default_flow_style=False)

    def tearDown(self) -> None:
        # remove(join(self.fldr, "settings.yaml"))
        rmtree(join(gettempdir(), "configs"))

    def test_user_change_settings_false(self):
        user_change_settings(
            overwrite=False, household_settings=["FULFP"], persons_settings=["CIT", "DDRS"], dest_folder=self.fldr
        )

        with open(join(self.fldr, "settings.yaml")) as file:
            doc = yaml.full_load(file)

        self.assertNotIn("FULFP", doc["output_synthetic_population"]["households"]["columns"])
        self.assertNotIn("CIT", doc["output_synthetic_population"]["persons"]["columns"])
        self.assertNotIn("DDRS", doc["output_synthetic_population"]["persons"]["columns"])

    def test_user_change_settings_true(self):
        user_change_settings(
            overwrite=True, household_settings=["FULFP"], persons_settings=["CIT", "DDRS"], dest_folder=gettempdir()
        )

        with open(join(self.fldr, "settings.yaml")) as file:
            doc = yaml.full_load(file)

        self.assertIn("FULFP", doc["output_synthetic_population"]["households"]["columns"])
        self.assertIn("CIT", doc["output_synthetic_population"]["persons"]["columns"])
        self.assertIn("DDRS", doc["output_synthetic_population"]["persons"]["columns"])


if __name__ == "__name__":
    unittest.main()
