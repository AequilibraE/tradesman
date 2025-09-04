import geopandas as gpd
import logging
import sys
from aequilibrae.context import get_logger
from aequilibrae.project import Project
from os.path import isdir

from tradesman.data_retrieval.import_build_and_places import ImportBuildPlaces
from tradesman.data_retrieval.microsoft_building_data import ImportMicrosoftBuildingData
from tradesman.model_creation.build_zoning import ZoneBuilder
from tradesman.model_creation.create_new_tables import add_new_tables
from tradesman.model_creation.import_network import ImportNetwork
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions
from tradesman.model_creation.import_population import ImportPopulation
from tradesman.model_creation.synthetic_population.create_synthetic_population import create_syn_pop, run_populationsim
from tradesman.utils import get_subdivisions


class Tradesman:
    def __init__(
        self,
        network_path: str,
        model_place: str = None,
        pbf_path: str = None,
        box_side: int = 25,
        boundaries_source: str = "Overture",
        population_source: str = "WorldPop",
        logger=None,
    ):
        # TODO: If the model exists, you would only tell where it is (network_path),
        # and the software would check and populate the model place.
        self.__model_place = model_place
        self.__population_source = population_source
        self.__folder = network_path
        self.project = Project()
        self.__pbf_path = pbf_path
        self.box_side = box_side
        self.logger = logger or get_logger()

        self.__initialize_model()

        self._boundaries_source = boundaries_source
        self._boundaries = ImportPoliticalSubdivisions(self.__model_place, self.project, self._boundaries_source)

    def create(self):
        """Creates the entire model"""

        self.import_model_area()
        self.add_country_borders()
        self.import_subdivisions()
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

    def add_country_borders(self, overwrite: bool = False):
        """
        Retrieves country borders and adds to the model.

        Parameters:
            *overwrite* (:obj:`bool`): User option for overwriting data that may already exist in the model.
            Defaults to ``False``
        """

        self._boundaries.add_country_borders(overwrite)

    def import_network(self):
        """
        Triggers the import of the network from OSM and adds subdivisions into the model.
        If the network already exists in the folder, it will be loaded, otherwise it will be created.
        """

        network = ImportNetwork(self.project, self.__model_place, self.__pbf_path, self.box_side)
        network.build_network()

    def import_subdivisions(self, subdivision_levels: int = 2, overwrite: bool = False):
        """Imports political subdivisions.

        Parameters:
            *subdivisions* (:obj:`int`): Number of subdivision levels to import. Defaults to 2

            *overwrite* (:obj:`bool`): Deletes pre-existing subdivisions. Defaults to False
        """

        self._boundaries.import_subdivisions(subdivision_levels, overwrite)

    def import_population(self):
        """
        Triggers the import of population from raster into the model.
        """

        population = ImportPopulation(self.project, self.__population_source)
        population.get_overall_population()

    def build_zoning(
        self,
        hexbin_size: int = 200,
        max_zone_pop: int = 10000,
        min_zone_pop: int = 500,
        save_hexbins: bool = False,
        overwrite: bool = False,
    ):
        """
        Creates hexagonal bins, and then clusters it regarding the political subdivision.

        Parameters:
            *hexbin_size*(:obj:`int`): size of the hexagonal bins to be created.

            *max_zone_pop*(:obj:`int`): max population living within a zone.

            *min_zone_pop*(:obj:`int`): min population living within a zone.

            *save_hexbins*(:obj:`bool`): saves the hexagonal bins with population. Defaults to ``False``.

            *overwrite* (:obj:`bool`): Deletes pre-existing HexBins and Zones. Defaults to ``False``.
        """
        if not overwrite and not self.project.zones.zoning.data.empty:
            raise ValueError("Project zones is not empty. Set overwrite=True to proceed.")

        zones = ZoneBuilder(self.project, hexbin_size, max_zone_pop, min_zone_pop, save_hexbins)
        zones.execute()

    def get_political_subdivisions(self, level: int = None) -> gpd.GeoDataFrame:
        """
        Return political subdivisions from a country.

        Parameters:
            *level*(:obj:`int`): Number of subdivision levels to import. Default imports all levels.
        """

        subd = get_subdivisions(self.project)
        if level is not None:
            subd = subd[subd.level == level]
        return subd

    def close(self):
        """
        Close the project model.
        """
        self.project.close()

    def import_pop_by_sex_and_age(self):
        """
        Triggers the import of population pyramid from raster into the model.
        """
        population = ImportPopulation(self.project)
        population.get_stratified_population()

    def import_amenities(self, box_side: int = 25):
        """
        Triggers the import of amenities from OSM.
        Data will be exported as columns in zones file and as a separate parquet file.

        Parameters:
            **box_size**(:obj:`int`): size of the box to be created (in km)
        """
        ovm = ImportBuildPlaces(self.project, box_side)
        ovm.import_places()

    def import_buildings(self, box_side: int = 25, download_from_mcr: bool = True):
        """
        Triggers the import of buildings from both Overture and Microsoft Bing.
        Data will be exported as columns in zones file and as a separate parquet file.

        Parameters:
            **box_size**(:obj:`int`): size of the box to be created (in km)

            **download_from_mcr**(:obj:`bool`): downloads building data from Microsoft Bing. Defaults to ``True``.
        """
        if download_from_mcr:
            mcr_bld = ImportMicrosoftBuildingData(self.project)
            mcr_bld.get_buildings()

        ovm = ImportBuildPlaces(self.project, box_side)
        ovm.import_building()

    def build_population_synthesizer_data(self, sample_size: float = 0.01):
        """
        Triggers the import of data to create the synthetic population.
        """
        create_syn_pop(self.project, self.__folder, sample_size=sample_size)

    def synthesize_population(self, thread_number: int = None, multithread: bool = False):
        """
        Triggers the creation of synthetic population.

        Parameters:
            *multithread*(:obj:`bool`): sets if one wants to use multiple threads or not. Defaults to False.

            *thread_number*(:obj:`int`): number of threads for multiprocessing
        """

        run_populationsim(multithread, self.project, self.__folder, thread_number)

    def __initialize_model(self):
        if isdir(self.__folder):
            self.project.open(self.__folder)
        else:
            self.project.new(self.__folder)
            with self.project.db_connection as conn:
                add_new_tables(conn)

    @property
    def place(self):
        """Returns the name of the place for which this model was made"""
        return self.__model_place

    # @staticmethod
    # def __starts_logging():
    #     logger = logging.getLogger("tradesman")
    #     stdout_handler = logging.StreamHandler(sys.stdout)
    #     formatter = logging.Formatter("%(asctime)s;%(name)s;%(message)s")
    #     stdout_handler.setFormatter(formatter)
    #     stdout_handler.name = "terminal"

    #     for handler in logger.handlers:
    #         if handler.name == "terminal":
    #             return
    #     logger.addHandler(stdout_handler)
