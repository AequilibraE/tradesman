import os
from pathlib import Path

from aequilibrae.project import Project
from aequilibrae.utils.create_example import create_example
from aequilibrae.utils.db_utils import commit_and_close
import pandas as pd


def create_example(path: os.PathLike) -> Project:
    """Copies an example model to a new project project and returns the project handle

    :Arguments:
        **path** (:obj:`str`): Path where to create a new model. Must be a non-existing folder/directory.

    :Returns:
        **project** (:obj:`Project`): AequilibraE Coquimbo Project handle (open)

    """
    pth = Path(path)
    if pth.is_dir() and pth.exists():
        raise FileExistsError("Cannot overwrite an existing directory")

    source = Path(__file__).parent / "reference_files" / "coquimbo.csv"
    population = pd.read_csv(source)
    
    project = create_example(path, "coquimbo")
    db_path = project.project_base_path / "project_database.sqlite"

    project_zones = project.zoning

    sex = {"f": "fe", "m": ""}
    age = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

    for key in sex.keys():
        for idx, a in enumerate(age):
            field_name = f"{key}_pop_{a}"
            if a < 80:
                project_zones.fields.add(field_name, f"{sex[key]}male population {a} to {age[idx+1]} years old.", "NUMERIC")
            else:
                project_zones.fields.add(field_name, f"{sex[key]}male population over {a} years old.", "NUMERIC")

            list_of_tuples = list(population[[field_name, "zone_id"]].itertuples(False, None))

            with commit_and_close(db_path, spatial=True) as conn:
                conn.executemany(f"UPDATE zones SET {field_name}=? WHERE zone_id=?;", list_of_tuples)
                conn.execute(f"UPDATE zones SET {field_name}=0 WHERE {field_name} IS NULL;")

    return project