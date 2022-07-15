import geopandas as gpd
import urllib.request
from os.path import join, isfile
from tempfile import gettempdir

from tradesman.data_retrieval.country_main_area import get_main_area


def select_urban_areas(project):

    url = r"https://github.com/pedrocamargo/road_analytics/releases/download/v0.1/global_urban_extent.gpkg"

    dest_path = join(gettempdir(), "global_urban_extent.gpkg")

    if not isfile(dest_path):
        urllib.request.urlretrieve(url, dest_path)

    country_borders = get_main_area(project)

    # gdf = gpd.GeoDataFrame(pd.DataFrame(country_borders, columns=['geometry']), geometry='geometry', crs=4326)

    urban_areas = gpd.read_file(url, mask=country_borders)

    return urban_areas
