from aequilibrae import Project
from tradesman.data_retrieval.osm_tags.import_osm_data import ImportOsmData


def import_amenities(project: Project, osm_data: dict):
    """
    Import and save OSM amenities into project.

    Parameters:
         *project*(:obj:`aequilibrae.project): current project.
         *osm_data*(:obj:`dict`): stores downloaded data.
    """
    ImportOsmData(tag="amenity", project=project, osm_data=osm_data).import_osm_data()
