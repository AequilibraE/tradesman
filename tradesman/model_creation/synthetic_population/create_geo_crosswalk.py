import csv
from os.path import join
import pandas as pd
from aequilibrae import Project


def create_geo_cross_walk(project: Project, dest_folder: str):
    """
    Creates the geographic controls over which PopulationSim will generate the synthetic population.
    Parameters:
         *project*(:obj:`aequilibrae.Project`): current project
         *dest_folder*(:obj:`str`): folder containing PopulationSim population files
    """

    qry = "SELECT zone_id AS TAZ, 1 PUMA, 1 REGION FROM zones;"
    pd.read_sql(qry, project.conn).to_csv(
        join(dest_folder, "data/geo_cross_walk.csv"), index=False, quoting=csv.QUOTE_NONNUMERIC
    )
