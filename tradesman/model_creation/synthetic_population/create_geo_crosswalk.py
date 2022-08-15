import csv
from aequilibrae import Project
from os.path import join


def create_geo_cross_walk(project: Project):

    qry = "SELECT zone_id FROM zones;"

    zone_id = project.conn.execute(qry).fetchall()

    regions_and_pumas = [1 for i in list(range(len(zone_id)))]

    create_lines = list(zip(zone_id, regions_and_pumas, regions_and_pumas))

    # TODO: fix temporary folder location
    folder = ""

    with open(join(folder, "geo_cross_walk.csv"), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(['"TAZ"', '"PUMA"', '"REGION"'])
        for line in create_lines:
            writer.writerow(line)

    print("geo_cross_walk.csv file created.")
