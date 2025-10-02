import pandas as pd
from aequilibrae.utils.create_example import create_example
from aequilibrae.utils.db_utils import commit_and_close

from tradesman.model_creation.create_new_tables import add_new_tables


def test_add_new_tables(folder_path):
    test_model = create_example(folder_path)

    db_path = test_model.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        add_new_tables(conn)

        df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)

    for i in ["political_subdivisions", "raw_population", "hex_pop"]:
        assert i in df.name.tolist()
