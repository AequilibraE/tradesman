from os.path import join, exists
from pathlib import Path

from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk


def test_create_geo_cross_walk(nauru_no_pop, folder_path):
    Path(join(folder_path, "data")).mkdir(parents=True, exist_ok=True)

    create_geo_cross_walk(nauru_no_pop, folder_path)
    assert exists(join(folder_path, "data/geo_cross_walk.csv"))
