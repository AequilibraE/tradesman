import logging
import sys
from os.path import isdir

import geopandas as gpd
from aequilibrae import Project

from tradesman.data_retrieval import subdivisions
from tradesman.data_retrieval.import_amenities import import_amenities
from tradesman.data_retrieval.import_building import building_import
from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_network import ImportNetwork
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.import_population import import_population
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age
from tradesman.model_creation.set_source import set_political_boundaries_source, set_population_source
from tradesman.model_creation.synthetic_population.create_synthetic_population import create_syn_pop, run_populationsim
from tradesman.model_creation.zoning.zone_building import zone_builder


class Tradesman:
    def __init__(
        self, network_path: str, model_place: str = None, pbf_path: str = None, boundaries_source: str = "GADM"
    ):
        # If the model exists, you would only tell where it is (network_path), and the software
        # would check and populate the model place.  Needs to be implemented
        self.__model_place = model_place
        self.__population_source = "WorldPop"
        self.__folder = network_path
        self._project = Project()
        self.__osm_data = {}
        self.__pbf_path = pbf_path
        self.__starts_logging()

        self.__initialize_model()
        self._network = ImportNetwork(self._project, self.__model_place, self.__pbf_path)

        self._boundaries_source = boundaries_source
        self._boundaries = ImportPoliticalSubdivisions(self.__model_place, self._boundaries_source, self._project)

    def create(self):
        """Creates the entire model"""

        self.import_model_area()
        self.add_country_borders()
        self.import_subdivisions(2)
        self.import_network()
        self.import_population()
        self.build_zoning()
        self.import_pop_by_sex_and_age()
        self.import_amenities()
        self.import_buildings(True)

    def import_model_area(self):
        """
        Retrieve model area.
        """

        self._boundaries.import_model_area()

    def add_country_borders(self, overwrite=False):
        """
        Retrieves country borders and adds to the model.

        Parameters:
            *overwrite* (:obj:`bool`): User option for overwriting data that may already exist in the model. Defaults to False
        """

        self._boundaries.add_country_borders(overwrite)

    def set_population_source(self, source="WorldPop"):
        """
        Sets the source for downloading population data

        Parameters:
            *source* (:obj:`str`): Can be 'WorldPop' or 'Meta'. Defaults to WorldPop
        """
        self.__population_source = set_population_source(source)

    def set_political_boundaries_source(self, source="GADM"):
        """
        Sets the source for downloading geographic data.

        Parameters:
             *source*(:obj:`str`): Takes "GADM" or "GeoBoundaries". Defaults to GADM.
        """
        self._boundaries_source = set_political_boundaries_source(source)

    def import_network(self):
        """
        Triggers the import of the network from OSM and adds subdivisions into the model.
        If the network already exists in the folder, it will be loaded, otherwise it will be created.
        """

        self._network.build_network()

    def import_subdivisions(self, subdivision_levels=2, overwrite=False):
        """Imports political subdivisions.

        Parameters:
            *subdivisions* (:obj:`int`): Number of subdivision levels to import. Defaults to 2
            *overwrite* (:obj:`bool`): Deletes pre-existing subdivisions. Defaults to False

        """

        self._boundaries.import_subdivisions(subdivision_levels, overwrite)

    def import_population(self, overwrite=False):
        """
        Triggers the import of population from raster into the model

        Parameters:
            *overwrite* (:obj:`bool`): Deletes pre-existing population_source_import. Defaults to False
        """

        fields = self._project.zoning.fields
        if "population" not in fields.all_fields():
            fields.add("population", "Total population", "INTEGER")
            fields.save()

        import_population(
            self._project, self._project.about.country_name, self.__population_source, overwrite=overwrite
        )

    def build_zoning(self, hexbin_size=200, max_zone_pop=10000, min_zone_pop=500, save_hexbins=False, overwrite=False):
        """
        Creates hexagonal bins, and then clusters it regarding the political subdivision.

        Parameters:
             *hexbin_size*(:obj:`int`): size of the hexagonal bins to be created.
             *max_zone_pop*(:obj:`int`): max population living within a zone.
             *min_zone_pop*(:obj:`int`): min population living within a zone.
             *save_hexbins*(:obj:`bool`): saves the hexagonal bins with population. Defaults to False.
             *overwrite* (:obj:`bool`): Deletes pre-existing HexBins and Zones. Defaults to False
        """

        if not overwrite and sum(self._project.conn.execute("Select count(*) from Zones").fetchone()) > 0:
            return
        zone_builder(self._project, hexbin_size, max_zone_pop, min_zone_pop, save_hexbins)

    def get_political_subdivisions(self, level: int = None) -> gpd.GeoDataFrame:
        """
        Return political subdivisions from a country.

        Parameters:
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
        get_pop_by_sex_age(self._project, self._project.about.country_name)

    def import_amenities(self):
        """
        Triggers the import of amenities from OSM.
        Data will be exported as columns in zones file and as a separate SQL file.
        """

        import_amenities(self._project, self.__osm_data)

    def import_buildings(self, download_from_bing=True):
        """
        Triggers the import of buildings from both OSM and Microsoft Bing.
        Data will be exported as columns in zones file and as a separate SQL file.

        Parameters:
            *download_from_bing(:obj:`bool`): downloads building data from Microsoft Bing. Defaults to True.
        """

        building_import(self.__model_place, self._project, self.__osm_data, download_from_bing)

    def build_population_synthesizer_data(self, sample_size=0.01):
        """
        Triggers the import of data to create the synthetic population.
        """
        create_syn_pop(self._project, self.__folder, sample_size=sample_size)

    def synthesize_population(self, thread_number=None, multithread=False):
        """
        Triggers the creation of synthetic population.

        Parameters:
            *multithread*(:obj:`bool`): sets if one wants to use multiple threads or not. Defaults to False.
            *thread_number*(:obj:`int`): number of threads for multiprocessing
        """

        run_populationsim(multithread, self._project, self.__folder, thread_number)

    def __initialize_model(self):
        if isdir(self.__folder):
            self._project.open(self.__folder)
        else:
            self._project.new(self.__folder)
            add_new_tables(self._project.conn)

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
