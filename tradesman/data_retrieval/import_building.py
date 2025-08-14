from aequilibrae.project import Project

from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData
from tradesman.data_retrieval.osm_tags.microsoft_building_footprint import ImportMicrosoftBuildingData


def building_import(project: Project, osm_data: dict, download_from_mcr: bool = True):
    """
    Import and save Microsoft Bing and OSM buildings into project.

    Parameters:
        *model_place*(:obj:`str`): current model place
        *project*(:obj:`aequilibrae.project): current project.
        *osm_data*(:obj:`dict`): stores downloaded data.
        *download_from_mcr(:obj:`bool`): downloads building data from Microsoft Bing. Defaults to True.
    """

    if download_from_mcr:
        mcr_bld = ImportMicrosoftBuildingData(project)
        mcr_bld.get_buildings()

    ImportOsmData(tag="building", project=project, osm_data=osm_data).import_osm_data()
