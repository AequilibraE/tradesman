import os
from aequilibrae.project.database_connection import database_connection, ENVIRON_VAR


def return_validation():

    folder = os.path.join(os.environ.get(ENVIRON_VAR), "synthetic_pop")

    pass
