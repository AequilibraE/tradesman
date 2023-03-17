import pytest

from tradesman.utils.create_tradesman_example import create_tradesman_example


def test_create_tradesman_example(create_path):
    prj = create_tradesman_example(create_path)
    cnx = prj.conn

    assert cnx.execute("SELECT COUNT(*) FROM zones;").fetchone()[0] == 13
    assert cnx.execute("SELECT COUNT(*) FROM political_subdivisions;").fetchone()[0] == 16
    assert cnx.execute("SELECT COUNT(*) FROM osm_building").fetchone()[0] == 2491
    assert cnx.execute("SELECT COUNT(*) FROM osm_amenity").fetchone()[0] == 29
    assert cnx.execute("SELECT COUNT(*) FROM synthetic_households").fetchone()[0] == 3384
    assert cnx.execute("SELECT COUNT(*) FROM synthetic_persons").fetchone()[0] == 8969
