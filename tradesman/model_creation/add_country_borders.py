import pycountry
import requests
from shapely.geometry import Polygon, MultiPolygon


def get_borders_online(country_name: str):
    country_code = pycountry.countries.search_fuzzy(country_name)[0].alpha_3

    r = requests.get(f"https://www.geoboundaries.org/gbRequest.html?ISO={country_code}&ADM=ADM0")
    dlPath = r.json()[0]["gjDownloadURL"]
    geoBoundary = requests.get(dlPath).json()
    if not geoBoundary["features"]:
        return MultiPolygon([0])
    geo = geoBoundary["features"][0]["geometry"]
    return MultiPolygon([Polygon(poly[0]) for poly in geo["coordinates"]])


def add_country_borders_to_model(country_name: str, project, overwrite=False):
    project.conn.execute('CREATE TABLE IF NOT EXISTS country_borders("country_name" TEXT);')

    if not overwrite:
        if sum(project.conn.execute("SELECT count(*) FROM country_borders").fetchone()) > 0:
            return

    geo = get_borders_online(country_name)

    project.conn.execute("DELETE FROM country_borders;")
    project.conn.execute("SELECT AddGeometryColumn( 'country_borders', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );")

    project.conn.execute("SELECT CreateSpatialIndex( 'country_borders' , 'geometry' );")
    project.conn.commit()

    sql = "INSERT into country_borders(country_name, geometry) VALUES(?, CastToMulti(GeomFromWKB(?, 4326)));"
    project.conn.execute(sql, [country_name, geo.wkb])
    project.conn.commit()
