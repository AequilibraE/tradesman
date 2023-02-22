import geopandas as gpd
import pytest

from tradesman.model_creation.zoning.create_clusters import create_clusters
from tradesman.model_creation.zoning.export_hex_population import saves_hex_pop_to_file
from tradesman.model_creation.zoning.export_zones import export_zones
from tradesman.model_creation.zoning.hex_builder import hex_builder
from tradesman.model_creation.zoning.zones_with_location import zones_with_location
from tradesman.model_creation.zoning.zones_with_pop import zones_with_population


@pytest.mark.parametrize("save_bins", [True, False])
def test_zone_builder(save_bins: bool, nauru_pop_test):
    sql = "SELECT division_name, level, Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions;"
    subdivisions = gpd.GeoDataFrame.from_postgis(sql, nauru_pop_test.conn, geom_col="geometry", crs=4326)
    subdivisions = subdivisions[subdivisions.level == subdivisions.level.max()]

    assert len(subdivisions) == 14

    sql = "SELECT division_name, level, Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where level = -1;"
    model_area = gpd.GeoDataFrame.from_postgis(sql, nauru_pop_test.conn, geom_col="geometry", crs=4326)
    if model_area.shape[0] > 0:
        subdivisions = subdivisions[subdivisions.intersects(model_area.geometry.unary_union)]

    assert len(model_area) == 1

    sql_coverage = (
        "SELECT Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where division_name='model_area';"
    )
    coverage_area = gpd.GeoDataFrame.from_postgis(sql_coverage, nauru_pop_test.conn, geom_col="geometry", crs=4326)
    coverage_area = coverage_area.explode().reset_index(drop=True).to_crs("epsg:3857")

    hexb = hex_builder(coverage_area, 100, epsg=3857)
    hexb.to_crs("epsg:4326", inplace=True)

    zones_with_locations = zones_with_location(hexb, subdivisions)

    zones_with_pop = zones_with_population(nauru_pop_test, zones_with_locations)

    if save_bins:
        saves_hex_pop_to_file(nauru_pop_test, zones_with_pop)

        assert nauru_pop_test.conn.execute("SELECT COUNT(*) FROM hex_pop;").fetchone()[0] > 0

    with pytest.raises(ValueError):
        clusters = create_clusters(zones_with_pop, 1, 10)

    clusters = create_clusters(zones_with_pop, 1000, 100)

    export_zones(clusters, nauru_pop_test)

    assert nauru_pop_test.conn.execute("SELECT COUNT(*) FROM zones;").fetchone()[0] > 10
