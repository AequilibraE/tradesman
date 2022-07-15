from aequilibrae import Project

from tradesman.model_creation.import_from_osm import import_net_from_osm


def trigger_network(project: Project, folder: str, model_place: str):
    print(folder)

    try:
        project.new(folder)

        import_net_from_osm(project, model_place)

    except FileNotFoundError:
        print("Location already exists. The existing directory will be loaded.")
        project.open(folder)
