import re
import pandas as pd
from aequilibrae import Project
from os.path import join


def create_geo_cross_walk(project: Project):

    qry = "SELECT zone_id FROM zones;"

    zone_id = project.conn.execute(qry).fetchall()
    
    regions_and_pumas = [1 for i in list(range(len(zone_id)))]

    create_lines = list(zip(zone_id, regions_and_pumas, regions_and_pumas))

    df = pd.DataFrame(create_lines, columns=['TAZ', '"PUMA"', '"REGION"'])

    folder = ""

    df.to_csv(join(folder, 'geo_cross_walk.txt'), sep=',', index=False, index_label=False)

    print("geo_cross_walk.txt file created.")