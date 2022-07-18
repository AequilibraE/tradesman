from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


def amenities(osm_data: dict, model_place: str, tile_size=25):
    """Finds all [amenities] (<https://wiki.openstreetmap.org/wiki/Key:amenity>) with a certain type for the
        model area.

    Args:
        *tile_size* (:obj:`float`): The size of the tile we want to split our area in. Defaults to 25km side
    """
    queries = [
        '[out:json][timeout:180];(node["amenity"]["area"!~"yes"]' + "({});>;);out geom;",
        '[out:json][timeout:180];(way["amenity"]["area"!~"yes"]' + "({});>;);out geom;",
    ]

    load_osm_data(
        tag="amenity",
        tile_size=tile_size,
        queries=queries,
        model_place=model_place,
        osm_data=osm_data,
    )

    return osm_data["amenity"]
