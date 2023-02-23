from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data
from aequilibrae.project import Project


def generic_tag(tag: str, osm_data: dict, project: Project, tile_size=25):
    """
    Finds all [amenity] (<https://wiki.openstreetmap.org/wiki/Key:amenity>)  or [building] (<https://wiki.openstreetmap.org/wiki/Key:building>) for the model area.

    Parameters:
         *tag*(:obj:`str`): download objects from Open Street Maps. Takes amenity or building.
         *osm_data*(:obj:`dict`): stores downloaded data.
         *project*(:obj:`aequilibrae.project): currently open project.
         *tile_size*(:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side.
    """
    queries = [
        f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
    ]

    load_osm_data(
        tag=tag,
        tile_size=tile_size,
        queries=queries,
        project=project,
        osm_data=osm_data,
    )

    return osm_data[f"{tag}"]
