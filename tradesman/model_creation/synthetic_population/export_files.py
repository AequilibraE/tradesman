from aequlibrae.project import Project
import pandas as pd
import sqlite3
from os.path import join


def export_syn_pop_data(project: Project, folder: str):

    persons = pd.read_csv(join(folder, "output/synthetic_persons.csv"))

    persons.to_sql("synthetic_persons", con=project.conn, if_exists="replace")

    households = pd.read_csv(join(folder, "output/synthetic_households.csv"))

    households.to_sql("synthetic_households", con=project.conn, if_exists="replace")
