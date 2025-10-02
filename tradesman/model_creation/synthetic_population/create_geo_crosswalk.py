import csv
from os.path import join

import pandas as pd
from aequilibrae import Project
from aequilibrae.utils.db_utils import commit_and_close


def create_geo_cross_walk(project: Project, dest_folder: str):
    """
    Creates the geographic controls over which PopulationSim will generate the synthetic population.
    Parameters:
         *project*(:obj:`aequilibrae.Project`): current project
         *dest_folder*(:obj:`str`): folder containing PopulationSim population files
    """
    db_path = project.project_base_path / "project_database.sqlite"
    with commit_and_close(db_path, spatial=True) as conn:
        qry = "SELECT zone_id AS TAZ, 1 PUMA, 1 REGION FROM zones;"
        pd.read_sql(qry, conn).to_csv(
            join(dest_folder, "data/geo_cross_walk.csv"), index=False, quoting=csv.QUOTE_NONNUMERIC
        )
