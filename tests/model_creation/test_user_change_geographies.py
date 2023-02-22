from os import rename
from os.path import join
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
import unittest
import yaml

from tradesman.model_creation.synthetic_population.user_control_import import user_change_geographies


class TestUsarChangeGeographies(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        self.fldr = join(gettempdir(), "configs")
        rename(temp_fldr, self.fldr)

        with open(join(self.fldr, "settings.yaml"), mode="w") as file:
            yaml.dump(
                dict(seed_geography="PUMA", geographies=["REGION", "PUMA", "TAZ"]), file, default_flow_style=False
            )

    def tearDown(self) -> None:
        # remove(join(self.fldr, "settings.yaml"))
        rmtree(join(gettempdir(), "configs"))

    def test_user_change_geographies_false(self):
        user_change_geographies(
            overwrite=False,
            seed_geography="COUNTY",
            upper_geography="STATE",
            lower_geography="DISTRICT",
            dest_folder=gettempdir(),
        )

        with open(join(self.fldr, "settings.yaml")) as file:
            doc = yaml.full_load(file)

        self.assertEqual(doc["seed_geography"], "PUMA")
        self.assertEqual(doc["geographies"], ["REGION", "PUMA", "TAZ"])

    def test_user_change_geographies_true(self):
        user_change_geographies(
            overwrite=True,
            seed_geography="COUNTY",
            upper_geography="STATE",
            lower_geography="DISTRICT",
            dest_folder=gettempdir(),
        )

        with open(join(self.fldr, "settings.yaml")) as file:
            doc = yaml.full_load(file)

        self.assertEqual(doc["seed_geography"], "COUNTY")
        self.assertEqual(doc["geographies"], ["STATE", "COUNTY", "DISTRICT"])


if __name__ == "__name__":
    unittest.main()
