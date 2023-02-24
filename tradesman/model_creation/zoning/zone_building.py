import geopandas as gpd

from tradesman.model_creation.zoning.create_clusters import create_clusters
from tradesman.model_creation.zoning.export_hex_population import saves_hex_pop_to_file
from tradesman.model_creation.zoning.export_zones import export_zones
from tradesman.model_creation.zoning.hex_builder import hex_builder
from tradesman.model_creation.zoning.zones_with_location import zones_with_location
from tradesman.model_creation.zoning.zones_with_pop import zones_with_population
from time import gmtime, strftime


def zone_builder(project, hexbin_size: int, max_zone_pop: int, min_zone_pop: int, save_hexbins: bool):
    """
    Build Traffic Analysis Zones.

    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project
         *hexbin_size*(:obj:`int`): size of the hexbin size. Defaults to 200
         *max_zone_pop*(:obj:`int`): max population within a zone. Defaults to 10,000
         *min_zone_pop*(:obj:`int`): min population within a zone. Defaults to 500
         *save_hexbins*(:obj:`bool`): saves hexbins with population. Defaults to False
    """

    sql = "SELECT division_name, level, Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions;"
    subdivisions = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geometry", crs=4326)
    subdivisions = subdivisions[subdivisions.level == subdivisions.level.max()]

    sql = "SELECT division_name, level, Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where level = -1;"
    model_area = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geometry", crs=4326)
    if model_area.shape[0] > 0:
        subdivisions = subdivisions[subdivisions.intersects(model_area.geometry.unary_union)]

    sql_coverage = (
        "SELECT Hex(ST_AsBinary(geometry)) as geometry FROM political_subdivisions where division_name='model_area';"
    )
    coverage_area = gpd.GeoDataFrame.from_postgis(sql_coverage, project.conn, geom_col="geometry", crs=4326)
    coverage_area = coverage_area.explode(index_parts=True).reset_index(drop=True).to_crs("epsg:3857")

    hexb = hex_builder(coverage_area, hexbin_size, epsg=3857)
    hexb.to_crs("epsg:4326", inplace=True)

    zones_with_locations = zones_with_location(hexb, subdivisions)

    zones_with_pop = zones_with_population(project, zones_with_locations)

    sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=' hex_pop';"
    if sum(project.conn.execute(sql).fetchone()) > 0:
        project.conn.execute("DELETE FROM hex_pop;")
    project.conn.execute("DELETE FROM zones;")
    project.conn.commit()
    if save_hexbins:
        saves_hex_pop_to_file(project, zones_with_pop)

    clusters = create_clusters(zones_with_pop, max_zone_pop, min_zone_pop)

    export_zones(clusters, project)
