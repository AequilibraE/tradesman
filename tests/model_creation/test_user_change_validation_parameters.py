from os import remove
import unittest
import yaml
from os.path import join
from tempfile import gettempdir

from tradesman.model_creation.synthetic_population.user_control_import import user_change_validation_parameters


class TestUserChangeValidationParameters(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = gettempdir()
        self.model_place = "Nauru"

        with open(join(self.fldr, "verification.yaml"), mode="w") as file:
            yaml.dump(
                dict(popsim_dir="", region="", validation_dir="", aggregate_summaries="", group_geographies=""),
                file,
                default_flow_style=False,
            )

    def tearDown(self) -> None:
        remove(join(self.fldr, "verification.yaml"))

    def test_user_change_validation_parameters_false(self):
        user_change_validation_parameters(overwrite=False, model_place=self.model_place, dest_folder=self.fldr)

        with open(join(gettempdir(), "verification.yaml"), mode="r") as file:
            doc = yaml.full_load(file)

        self.assertEqual(doc["popsim_dir"], "population")
        self.assertEqual(doc["region"], self.model_place)
        self.assertEqual(doc["validation_dir"], "validation_results")

    def test_user_change_validation_parameters_true(self):
        user_change_validation_parameters(
            overwrite=True,
            model_place=self.model_place,
            dest_folder=self.fldr,
            aggregate_summaries=[
                {
                    "name": "citzenship_status",
                    "geography": "COUNTY",
                    "control": "citz_status_control",
                    "result": "citz_status_result",
                }
            ],
            geographies=["STATE", "COUNTY", "DISTRICT"],
        )

        with open(join(gettempdir(), "verification.yaml"), mode="r") as file:
            doc = yaml.full_load(file)

        self.assertEqual(
            doc["aggregate_summaries"],
            [
                {
                    "name": "citzenship_status",
                    "geography": "COUNTY",
                    "control": "citz_status_control",
                    "result": "citz_status_result",
                }
            ],
        )
        self.assertEqual(doc["group_geographies"], ["STATE", "COUNTY", "DISTRICT"])


if __name__ == "__name__":
    unittest.main()
