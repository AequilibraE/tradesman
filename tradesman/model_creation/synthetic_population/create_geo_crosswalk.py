import csv
from os.path import join
import pandas as pd
from aequilibrae import Project


def create_geo_cross_walk(project: Project, file_folder: str):

    qry = "SELECT zone_id AS TAZ, 1 PUMA, 1 REGION FROM zones;"
    pd.read_sql(qry, project.conn).to_csv(join(file_folder, "data/geo_cross_walk.csv"), index=False, quoting=csv.QUOTE_NONNUMERIC)

    print("geo_cross_walk.csv file created.")
