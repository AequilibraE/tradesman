import pytest

from tradesman.data_retrieval.osm_tags.osm_load_data import load_osm_data


@pytest.mark.parametrize("tag", ["amenity", "building"])
def test_load_osm_data(tag: str, nauru_test):
    osm_data = {}
    query = [
        f'[out:json][timeout:180];(node["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
        f'[out:json][timeout:180];(way["{tag}"]["area"!~"yes"]' + "({});>;);out geom;",
    ]

    load_osm_data(tag=tag, osm_data=osm_data, queries=query, project=nauru_test, tile_size=25)

    assert osm_data, {tag: []}
