import multiprocessing as mp
import subprocess
import yaml
from os.path import join
import pandas as pd
import sys

from aequilibrae.project import Project
from tradesman.model_creation.synthetic_population.create_control_totals_meta import create_control_totals_meta
from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz
from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk
from tradesman.model_creation.synthetic_population.create_seeds import create_buckets
from tradesman.model_creation.synthetic_population.syn_pop_validation import (
    validate_controlled_vars,
    validate_non_controlled_vars,
)
from tradesman.model_creation.synthetic_population.unzip_files import unzip_control_and_seed_files
from tradesman.model_creation.synthetic_population.user_control_import import user_change_validation_parameters


def create_syn_pop(project: Project, model_place: str, cwd: str, thread_number=None):
    """
    Creates synthetic population to be used im Activity Based Models, using PopulationSim.

    Args:
         *project*(:obj:`aequilibrae.project`):
         *model_place*(:obj:`str`):
         *folder*(:obj:`str`):
         *thread_number*(:obj:`int`):

    """

    unzip_control_and_seed_files(cwd)

    pop_fldr = join(cwd, "population")

    set_thread_number(pop_fldr, thread_number)

    create_buckets(model_place, project, folder=pop_fldr, sample=0.02)

    create_geo_cross_walk(project, pop_fldr)

    create_control_totals_taz(project, model_place, pop_fldr)

    create_control_totals_meta(pop_fldr)


def set_thread_number(folder: str, number):
    """
    Set the number of threads to generate the synthetic population.
    If no number of threads is provides, the program considers it as the number of threads available in your computer.

    Args:
         *folder*(:obj:`str`): folder where the project files are.
         *number*(:obj:`int`): number of threads used. By default uses the greatest number of threads available.

    """

    count_cpu = mp.cpu_count()
    if number is None or int(number) > count_cpu or number == 0:
        number = mp.cpu_count()
    else:
        number = int(number)

    with open(join(folder, "configs/settings.yaml"), encoding="utf-8") as file:
        doc = yaml.full_load(file)

    doc["num_processes"] = number

    with open(join(folder, "configs/settings.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(doc, file, default_flow_style=False)


def run_populationsim(project: Project, model_place: str, folder: str):
    """
    This function runs the module PopulationSim to generate synthetic populations, exports the results to the project database, and runs the validation process.
    Args:
         *project*:
         *model_place*:
         *folder*:
    """

    pop_fldr = join(folder, "population")

    user_change_validation_parameters(overwrite=False, model_place=model_place, dest_folder=pop_fldr)

    subprocess.run([sys.executable, "run_populationsim.py"], cwd=pop_fldr)

    pd.read_csv(join(pop_fldr, "output/synthetic_persons.csv")).to_sql(
        "synthetic_persons", con=project.conn, if_exists="replace"
    )

    pd.read_csv(join(pop_fldr, "output/synthetic_households.csv")).to_sql(
        "synthetic_households", con=project.conn, if_exists="replace"
    )

    validate_non_controlled_vars(model_place, pop_fldr)

    validate_controlled_vars(pop_fldr)
