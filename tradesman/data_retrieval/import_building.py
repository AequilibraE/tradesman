from aequilibrae.project import Project

from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData
from tradesman.data_retrieval.osm_tags.microsoft_building_footprint import ImportMicrosoftBuildingData


def building_import(model_place: str, project: Project, osm_data: dict, download_from_bing=True):
    """
    Import and save Microsoft Bing and OSM buildings into project.

    Parameters:
         *model_place*(:obj:`str`): current model place
         *project*(:obj:`aequilibrae.project): current project.
         *osm_data*(:obj:`dict`): stores downloaded data.
         *download_from_bing(:obj:`bool`): downloads building data from Microsoft Bing. Defaults to True.
    """

    if download_from_bing:
        mcsftbldg = ImportMicrosoftBuildingData(model_place, project)
        if mcsftbldg._available:
            mcsftbldg.microsoft_buildings()

    ImportOsmData(tag="building", project=project, osm_data=osm_data).import_osm_data()
