from aequilibrae.utils.create_example import create_example

from tradesman.model_creation.create_new_tables import add_new_tables


def create_nauru_test(folder):
    # Let's use the Nauru example project for display
    project = create_example(folder, "nauru")
    add_new_tables(project.conn)
