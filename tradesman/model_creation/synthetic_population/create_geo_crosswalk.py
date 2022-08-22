import csv
import pandas as pd
from aequilibrae import Project
from os.path import join


def create_geo_cross_walk(project: Project, file_folder: str):

    qry = "SELECT zone_id FROM zones;"

    zone_id = [i[0] for i in project.conn.execute(qry).fetchall()]

    regions_and_pumas = np.ones(len(zone_id))


    df = pd.DataFrame({"TAZ":zone_id, "PUMA":regions_and_pumas, "REGION":regions_and_pumas})

    qry = "SELECT zone_id TAZ, 1 PUMA, 1, REGION FROM zones;"
    pd.read_sql(qry, project.conn).to_csv("data/geo_cross_walk.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df.to_csv(
        join(file_folder, "data/geo_cross_walk.csv"),
        sep=",",
        index=False,
        index_label=None,
        quoting=csv.QUOTE_NONNUMERIC,
    )

    print("geo_cross_walk.csv file created.")
