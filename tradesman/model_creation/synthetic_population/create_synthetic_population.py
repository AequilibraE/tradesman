from math import floor
import multiprocessing as mp
import subprocess
import warnings
import yaml
from os.path import join, isfile
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
from tradesman.model_creation.synthetic_population.unzip_seed_files import unzip_seed_files
from tradesman.model_creation.synthetic_population.user_control_import import user_change_validation_parameters


def create_syn_pop(project: Project, cwd: str, sample_size=0.01):
    """
    Creates files to build synthetic population.

    Parameters:
        *project*(:obj:`aequilibrae.project`):
        *cwd*(:obj:`str`):
    """

    unzip_seed_files(cwd)

    pop_fldr = join(cwd, "population")

    create_buckets(project, folder=pop_fldr, sample=sample_size)

    create_geo_cross_walk(project, pop_fldr)

    create_control_totals_taz(project, pop_fldr)

    create_control_totals_meta(pop_fldr)


def update_thread_number(folder: str, number: int):
    """
    Set the number of threads to generate the synthetic population.
    If no number of threads is provided, the number of threads available in your computer is considered.

    Parameters:
        *folder*(:obj:`str`): folder where the project files are.
        *number*(:obj:`int`): number of threads used. By default uses the greatest number of threads available.
    """
    count_cpu = mp.cpu_count()
    if number is not None:
        floor_num = floor(number)
    pass

    if number is None:
        number = mp.cpu_count()
    elif floor_num > count_cpu or floor_num == 0:
        number = mp.cpu_count()
    else:
        number = floor_num

    with open(join(folder, "configs/settings.yaml"), encoding="utf-8") as file:
        doc = yaml.full_load(file)

    doc["num_processes"] = number

    with open(join(folder, "configs/settings.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(doc, file, default_flow_style=False)

    with open(join(folder, "configs_mp/settings.yaml"), encoding="utf-8") as file:
        doc = yaml.full_load(file)

    doc["num_processes"] = number
    doc["multiprocess_steps"][1]["num_processes"] = number

    with open(join(folder, "configs_mp/settings.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(doc, file, default_flow_style=False)


def run_populationsim(multithread: bool, project: Project, folder: str, thread_number=None):
    """
    Runs PopulationSim and exports the results to the project database.

    Parameters:
         *multithread*(:obj:`bool`): run PopulationSim with multi-threads. Defaults to False
         *project*(:obj:`aequilibrae.project`): currently open project
         *folder*(:obj:`str`): path to folder containing population info.
         *thread_number*(:obj:`int`): number of threads one wants to use.
    """
    pop_fldr = join(folder, "population")

    num_zones = project.conn.execute("SELECT COUNT(*) FROM zones;").fetchone()[0]

    if multithread or num_zones > 100:
        update_thread_number(pop_fldr, thread_number)
    else:
        update_thread_number(pop_fldr, number=1)

    subprocess.run(
        [sys.executable, "run_populationsim.py"], cwd=pop_fldr, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )

    if not isfile(join(pop_fldr, "output/final_summary_TAZ.csv")):
        warnings.warn(
            "Synthetic population was not generated. Please increase your sample size or change the number of threads."
        )
        return

    pd.read_csv(join(pop_fldr, "output/synthetic_persons.csv"))[["hh_id", "TAZ", "AGEP", "SEX"]].to_sql(
        "synthetic_persons", con=project.conn, if_exists="replace"
    )

    pd.read_csv(join(pop_fldr, "output/synthetic_households.csv"))[["hh_id", "TAZ", "NP"]].to_sql(
        "synthetic_households", con=project.conn, if_exists="replace"
    )

    fields = [
        ("synthetic_persons", "hh_id", "household id"),
        ("synthetic_persons", "TAZ", "Unique Traffic Analysis Zones id"),
        ("synthetic_persons", "AGEP", "synthetic person age"),
        ("synthetic_persons", "SEX", "synthetic person sex"),
        ("synthetic_households", "hh_id", "household id"),
        ("synthetic_households", "TAZ", "Unique Traffic Analysis Zones id"),
        ("synthetic_households", "NP", "number of persons in the household"),
    ]

    project.conn.executemany(
        "INSERT INTO 'attributes_documentation' (name_table, attribute, description) VALUES (?, ?, ?);", fields
    )
    project.conn.commit()

    user_change_validation_parameters(overwrite=False, model_place=project.about.model_name, dest_folder=pop_fldr)

    validate_non_controlled_vars(project.about.country_code, pop_fldr)

    validate_controlled_vars(pop_fldr)
