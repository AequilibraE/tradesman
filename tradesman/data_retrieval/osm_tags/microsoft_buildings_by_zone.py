import io
import re
from tempfile import tempdir
import zipfile
import requests
from os.path import join
from bs4 import BeautifulSoup
import geopandas as gpd
from aequilibrae import Project
from tradesman.data.load_zones import load_zones


def microsoft_buildings_by_zone(model_place: str, project: Project):

    url = "https://github.com/microsoft/GlobalMLBuildingFootprints"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    if model_place in soup.find_all(string=re.compile(f"{model_place}")):
        downloadable_link = soup.find("td", string=f"{model_place}").find_next_siblings()[1].find("a")["href"]
    else:
        return ValueError("There is no available data for the country in Bing database.")

    r = requests.get(downloadable_link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    filename = z.namelist()[0]
    var = join(tempdir, z.extract(filename))

    model_gdf = gpd.read_file(var)

    model_gdf["area"] = model_gdf.to_crs(3857).geometry.area

    zones = load_zones(project)

    buildings_by_zone = gpd.sjoin(model_gdf, zones)

    buildings_by_zone.drop(columns=["index_right"], inplace=True)

    buildings_by_zone.insert(0, column="id", value=list(range(1, len(buildings_by_zone) + 1)))

    buildings_by_zone["geom"] = buildings_by_zone.geometry.to_wkb()

    print("Saving Microsoft buildings.")

    project.conn.execute("Drop TABLE IF EXISTS microsoft_buildings;")
    project.conn.execute(
        'CREATE TABLE IF NOT EXISTS microsoft_buildings("id" INTEGER, "area" FLOAT, "zone_id" INTEGER);'
    )
    project.conn.execute("SELECT AddGeometryColumn('microsoft_buildings', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );")

    project.conn.execute("SELECT CreateSpatialIndex( 'microsoft_buildings' , 'geometry' );")
    project.conn.commit()

    qry = """INSERT into microsoft_buildings(id, area, zone_id, geometry) VALUES(?, ?, ?, CastToMulti(GeomFromWKB(?, 4326)));"""
    list_of_tuples = list(buildings_by_zone[["id", "area", "zone_id", "geom"]].itertuples(index=False, name=None))
    project.conn.executemany(qry, list_of_tuples)
    project.conn.commit()

    return buildings_by_zone
