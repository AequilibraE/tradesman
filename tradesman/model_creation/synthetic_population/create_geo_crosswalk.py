import csv
import pandas as pd
from aequilibrae import Project
from os.path import join


def create_geo_cross_walk(project: Project, file_folder: str):

    qry = "SELECT zone_id FROM zones;"

    zone_id = [i[0] for i in project.conn.execute(qry).fetchall()]

    regions_and_pumas = [1 for i in list(range(len(zone_id)))]

    create_lines = list(zip(zone_id, regions_and_pumas, regions_and_pumas))

    df = pd.DataFrame(create_lines, columns=["TAZ", "PUMA", "REGION"])

    df.to_csv(
        join(file_folder, "data/geo_cross_walk.csv"),
        sep=",",
        index=False,
        index_label=None,
        quoting=csv.QUOTE_NONNUMERIC,
    )

    print("geo_cross_walk.csv file created.")
