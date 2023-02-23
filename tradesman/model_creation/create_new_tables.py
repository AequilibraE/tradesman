import glob
import sqlite3
from os.path import join, dirname


def add_new_tables(connection: sqlite3.Connection):
    """
    Creates Tradesman tables.

    Parameters:
        *connection*(:obj:`sqlite3.Connection`): valid sqlite3.Connection
    """
    cursor = connection.cursor()

    pth = join(dirname(__file__), "database_structure")
    for filename in glob.glob(join(pth, "*.sql")):
        with open(filename, "r") as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
    connection.commit()
