from os.path import abspath, dirname, join
from pathlib import Path
from shutil import copy

import pandas as pd

from tradesman.model_creation.synthetic_population.create_seeds import create_buckets


def test_create_seeds(nauru_no_pop, folder_path):
    Path(join(folder_path, "data")).mkdir(parents=True, exist_ok=True)

    copy(
        src=join(abspath(dirname("tests")),
                 "tests/data/nauru/population/data/seed_households.csv"),
        dst=join(folder_path, "data/seed_households.csv"),
    )
    copy(
        src=join(abspath(dirname("tests")),
                 "tests/data/nauru/population/data/seed_persons.csv"),
        dst=join(folder_path, "data/seed_persons.csv"),
    )

    create_buckets(nauru_no_pop, folder_path)
    x = len(pd.read_csv(join(folder_path, "data/seed_households.csv")))
    assert x > 70
