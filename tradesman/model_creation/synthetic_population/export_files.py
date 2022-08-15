from aequlibrae.project import Project
import pandas as pd
import sqlite3
from os.path import join


def export_syn_persons():

    path = ""

    df = pd.read_csv(join(path, "synthetic_persons.csv"))

    conn = sqlite3.connect(join(path, "project_database.sqlite"))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS synthetic_persons(puma INTEGER, \
                                                               taz INTEGER, \
                                                               household_id INTEGER, \
                                                               per_num INTEGER,\
                                                               age INTEGER,\
                                                               sex INTEGER,\
                                                               occp INTEGER);"
    )

    df.to_sql()
    pass


def export_syn_households():

    pass
