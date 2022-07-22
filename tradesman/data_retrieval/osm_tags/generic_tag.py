from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


def generic_tag(tag: str, osm_data: dict, model_place: str, tile_size=25):
    """
    Finds all [amenities] (<https://wiki.openstreetmap.org/wiki/Key:amenity>)  or [building] (<https://wiki.openstreetmap.org/wiki/Key:building>) with a certain type for the model area.

    Args:
        *tile_size* (:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side
    """
    queries = [
        f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
    ]

    load_osm_data(
        tag=tag,
        tile_size=tile_size,
        queries=queries,
        model_place=model_place,
        osm_data=osm_data,
    )

    return osm_data[f"{tag}"]
