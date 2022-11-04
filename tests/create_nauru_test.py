from math import sqrt
from os.path import dirname, join

import geopandas as gpd
import shapely.wkb
from aequilibrae.utils.create_example import create_example
from shapely.geometry import Point
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions

from tradesman.model_creation.create_new_tables import add_new_tables


def create_nauru_test(folder):
    df = gpd.read_file(join(dirname(__file__), "data/nauru/subdivisions.geojson"))
    df.rename(columns={"name": "division_name", "country": "country_name"}, inplace=True)
    df.insert(2, "level", 1)
    df["geom"] = gpd.GeoSeries.to_wkb(df["geometry"])

    project = create_example(folder, "nauru")
    add_new_tables(project.conn)

    data = ImportPoliticalSubdivisions(model_place="Nauru", project=project, source="GADM")
    data.import_model_area()
    data.add_country_borders(overwrite=True)

    zones = 12

    network = project.network

    geo = network.convex_hull()

    zone_area = geo.area / zones

    zone_side = sqrt(2 * sqrt(3) * zone_area / 9)

    extent = network.extent()

    curr = project.conn.cursor()
    b = extent.bounds
    curr.execute(
        "select st_asbinary(HexagonalGrid(GeomFromWKB(?), ?, 0, GeomFromWKB(?)))",
        [extent.wkb, zone_side, Point(b[2], b[3]).wkb],
    )
    grid = curr.fetchone()[0]
    grid = shapely.wkb.loads(grid)

    grid = [p for p in grid.geoms if p.intersects(geo)]

    nodes = network.nodes
    for i in range(1, 301):
        nd = nodes.get(i)
        nd.renumber(i + 1300)

    zoning = project.zoning
    for i, zone_geo in enumerate(grid):
        zone = zoning.new(i + 1)
        zone.geometry = zone_geo
        zone.save()

    zones_from_location = gpd.GeoDataFrame.from_postgis(
        "SELECT zone_id,  Hex(ST_AsBinary(geometry)) as geom FROM zones;", project.conn, geom_col="geom", crs=4326
    )

    population = [358, 686, 541, 966, 474, 158, 1088, 214, 1178, 473, 59, 1004, 186, 499, 331, 199, 763, 447, 222]

    qry_values = list(zip(population, zones_from_location.zone_id.values))

    project.conn.executemany("UPDATE zones SET population=? WHERE zone_id=?;", qry_values)
    project.conn.commit()

    project.conn.execute("DELETE FROM political_subdivisions WHERE level>0;")
    project.conn.commit()

    qry = "INSERT INTO political_subdivisions (country_name, division_name, level, geometry) \
            VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"
    list_of_tuples = list(df[["country_name", "division_name", "level", "geom"]].itertuples(index=False, name=None))

    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()

    return project
