from aequilibrae import Project

from tradesman.data_retrieval.osm_tags.import_osm_data import import_osm_data
from tradesman.data_retrieval.osm_tags.microsoft_buildings_by_zone import (
    microsoft_buildings_by_zone,
)

from tradesman.data_retrieval.osm_tags.microsoft_buildings_save import save_microsoft_buildings
from tradesman.data_retrieval.osm_tags.osm_buildings_save import save_osm_buildings


def building_import(model_place: str, project: Project, osm_data: dict, download_from_bing=True):
    """
    Import and save Microsoft Bing and OSM buildings into project.

    Parameters:
         *model_place*(:obj:`str`): current model place
         *project*(:obj:`aequilibrae.project): current project.
         *osm_data*(:obj:`dict`): stores downloaded data.
         *download_from_bing(:obj:`bool`): donwloads building data from Microsoft Bing. Defaults to True.
    """

    if download_from_bing:
        microsoft_buildings = microsoft_buildings_by_zone(model_place, project)

    if microsoft_buildings is None:
        pass
    else:
        save_microsoft_buildings(microsoft_buildings, project)

    osm_buildings = import_osm_data(tag="building", osm_data=osm_data, project=project)

    save_osm_buildings(osm_buildings, project)
