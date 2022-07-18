from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


def buildings(osm_data: dict, model_place: str, tile_size=25):
    """Finds all [buildings] (<https://wiki.openstreetmap.org/wiki/Key:building>) with a certain type for the
        model area.

    Args:
        *tile_size* (:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side
    """
    queries = [
        '[out:json][timeout:180];(node["building"]["area"!~"yes"]' + "({});>;);out geom;",
        '[out:json][timeout:180];(way["building"]["area"!~"yes"]' + "({});>;);out geom;",
    ]

    load_osm_data(
        tag="building",
        tile_size=tile_size,
        queries=queries,
        osm_data=osm_data,
        model_place=model_place,
    )

    return osm_data["building"]
