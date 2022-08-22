import multiprocessing as mp
import subprocess
import yaml
from os.path import join

from aequilibrae.project import Project
from tradesman.model_creation.synthetic_population.create_control_totals_meta import create_control_totals_meta
from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz
from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk
from tradesman.model_creation.synthetic_population.export_files import export_syn_pop_data
from tradesman.model_creation.synthetic_population.syn_pop_validation import validate_controlled_vars, validate_non_controlled_vars
from tradesman.model_creation.synthetic_population.unzip_files import unzip_control_and_seed_files
from tradesman.model_creation.synthetic_population.user_control_import import (
    user_change_geographies,
    user_change_settings,
    user_control_import,
    user_import_new_seeds,
    user_import_new_totals,
)


def create_syn_pop(project: Project, model_place: str, folder: str):
    """
    Creates synthetic population to be used im Activity Based Models, using PopulationSim.

    Args:
         *project*(:obj:`aequilibrae.project`):
         *model_place*(:obj:`str`):
         *folder*(:obj:`str`):

    """

    unzip_control_and_seed_files(file_path=folder)

    pop_fldr = join(folder, "population")

    user_control_import(overwrite=False, folder=pop_fldr)

    user_change_settings(overwrite=False, folder=pop_fldr)

    user_change_geographies(overwrite=False, folder=pop_fldr)

    user_import_new_seeds(overwrite=False, folder=pop_fldr)

    user_import_new_totals(overwrite=False, folder=pop_fldr)

    set_thread_number(pop_fldr)

    create_geo_cross_walk(project, pop_fldr)

    create_control_totals_taz(project, model_place, pop_fldr)

    create_control_totals_meta(pop_fldr)


def set_thread_number(folder: str, number=None):
    """
    Set the number of threads to generate the synthetic population.
    If no number of threads is provides, the program considers it as the number of threads available in your computer.

    Args:
         *folder*(:obj:`str`): folder where the project files are placed
         *number*(:obj:`int`): number of threads used. By default uses the greatest number of threads available.

    """
    if number is None:
        number = mp.cpu_count()

    with open(join(folder, "configs/settings.yaml"), encoding='utf-8') as file:
        doc = yaml.full_load(file)

    doc["num_processes"] = number

    with open(join(folder, "configs/settings.yaml"), "w", encoding='utf-8') as file:
        yaml.safe_dump(doc, file, default_flow_style=False)

def run_populationsim(project: Project, model_place: str, folder: str):
    """
    This function runs the module PopulationSim to generate synthetic populations, exports the results, and runs the validation process.
    Args:
         *project*:
         *model_place*:
         *folder*:
    """

    pop_fldr = join(folder, "population")

    subprocess.Popen(["python", "run_populationsim.py"], cwd=pop_fldr)

    export_syn_pop_data(project, pop_fldr)

    validate_controlled_vars(pop_fldr)

    validate_non_controlled_vars(model_place, pop_fldr)
