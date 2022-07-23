import logging
import sys
from os.path import isdir

import geopandas as gpd
from aequilibrae import Project

from tradesman.data_retrieval import subdivisions
from tradesman.data_retrieval.import_amenities import import_amenities
from tradesman.data_retrieval.import_building import building_import
from tradesman.model_creation.add_country_borders import add_country_borders_to_model
from tradesman.model_creation.get_country_subdivision import add_subdivisions_to_model
from tradesman.model_creation.import_network import import_network
from tradesman.model_creation.import_population import import_population
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age
from tradesman.model_creation.set_source import set_source
from tradesman.model_creation.zoning.zone_building import zone_builder


class Tradesman:
    def __init__(self, network_path: str, model_place: str = None):
        # If the model exists, you would only tell where it is (network_path), and the software
        # would check and populate the model place.  Needs to be implemented
        self.__model_place = model_place
        self.__population_source = "WorldPop"
        self.__folder = network_path
        self._project = Project()
        self.__osm_data = {}
        self.__starts_logging()

        self.__initialize_model()

    def create(self):
        """Creates the entire model"""

        self.add_country_borders()
        self.import_network()
        self.import_subdivisions(2, True)
        self.import_population()
        self.build_zoning()
        self.import_pop_by_sex_and_age()
        self.import_amenities()
        self.import_buildings()

    def add_country_borders(self, overwrite=False):
        """Retrieves country borders from www.geoboundarries.org and adds to the model.
        Args:
               *overwrite* (:obj:`bool`): User option for overwriting data that may already e3xist in the model. Defaults to False"""

        add_country_borders_to_model(self.__model_place, self._project, overwrite)

    def set_population_source(self, source="WorldPop"):
        """Sets the source for the raster population data
        Args:
               *source* (:obj:`str`): Can be 'WorldPop' or 'Meta'. Defaults to WorldPop
        """
        self.__population_source = set_source(source)

    def import_network(self):
        """Triggers the import of the network from OSM and adds subdivisions into the model.
        If the network already exists in the folder, it will be loaded, otherwise it will be created."""
        import_network(self._project, self.__model_place)

    def import_subdivisions(self, subdivision_levels=2, overwrite=False):
        """Imports political subdivisions.

        Args:
               *subdivisions* (:obj:`int`): Number of subdivision levels to import. Defaults to 2
               *overwrite* (:obj:`bool`): Deletes pre-existing subdivisions. Defaults to False

        """
        add_subdivisions_to_model(self._project, self.__model_place, subdivision_levels, overwrite)

    def import_population(self, overwrite=False):
        """
        Triggers the import of population from raster into the model

        Args:
                *overwrite* (:obj:`bool`): Deletes pre-existing population_source_import. Defaults to False
        """

        import_population(self._project, self.__model_place, self.__population_source, overwrite=overwrite)

    def build_zoning(self, hexbin_size=200, max_zone_pop=10000, min_zone_pop=500, save_hexbins=True):
        """Creates hexagonal bins, and then clusters it regarding the political subdivision.

        Args:
             *hexbin_size*(:obj:`int`): size of the hexagonal bins to be created.
             *max_zone_pop*(:obj:`int`): max population living within a zone.
             *min_zone_pop*(:obj:`int`): min population living within a zone.
             *save_hexbins*(:obj:`bool`): saves the hexagonal bins with population. Defaults to True.
        """

        zone_builder(self._project, hexbin_size, max_zone_pop, min_zone_pop, save_hexbins)

    def get_political_subdivisions(self, level: int = None) -> gpd.GeoDataFrame:
        """Return political subdivisions from a country.

        Args:
             *level*(:obj:`int`): Number of subdivision levels to import. Default imports all levels.
        """

        subd = subdivisions(self._project)
        if level is not None:
            subd = subd[subd.level == level]
        return subd

    def close(self):
        """
        Close the project model.
        """
        self._project.close()

    def import_pop_by_sex_and_age(self):
        """
        Triggers the import of population pyramid from raster into the model.
        """
        get_pop_by_sex_age(self._project, self.__model_place)

    def import_amenities(self):
        """
        Triggers the import of amenities from OSM.
        Data will be exported as columns in zones file and as a separate SQL file.
        """

        import_amenities(self.__model_place, self._project, self.__osm_data)

    def import_buildings(self):
        """
        Triggers the import of buildings from both OSM and Microsoft Bing.
        Data will be exported as columns in zones file and as a separate SQL file.
        """

        building_import(self.__model_place, self._project, self.__osm_data)

    def __initialize_model(self):
        if isdir(self.__folder):
            self._project.open(self.__folder)
        else:
            self._project.new(self.__folder)

    @property
    def place(self):
        """Returns the name of the place for which this model was made"""
        return self.__model_place

    @staticmethod
    def __starts_logging():
        logger = logging.getLogger("tradesman")
        stdout_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s;%(name)s;%(message)s")
        stdout_handler.setFormatter(formatter)
        stdout_handler.name = "terminal"

        for handler in logger.handlers:
            if handler.name == "terminal":
                return
        logger.addHandler(stdout_handler)
