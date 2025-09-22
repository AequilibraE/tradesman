from os.path import exists, join
from pathlib import Path

from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz


def test_create_control_totals_taz(nauru_no_pop, folder_path):
    Path(join(folder_path, "data")).mkdir(parents=True, exist_ok=True)

    create_control_totals_taz(nauru_no_pop, folder_path)
    assert exists(join(folder_path, "data/control_totals_taz.csv"))
