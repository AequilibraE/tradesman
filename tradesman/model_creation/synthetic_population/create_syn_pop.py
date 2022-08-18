import multiprocessing as mp
import subprocess
from os.path import join

# from os import mkdir
from aequilibrae.project import Project
from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk
from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz
from tradesman.model_creation.synthetic_population.create_control_totals_meta import create_control_totals_meta
from tradesman.model_creation.synthetic_population.export_files import export_syn_pop_data
from tradesman.model_creation.synthetic_population.unzip_files import unzip_control_files


def create_syn_pop(project: Project, model_place: str, folder: str):

    pop_fldr = join(folder, "population")  # Onde nossa população ficará

    # Seguindo o passo a passo do PopulationSim:
    # Primeiro criamos uma pasta junto ao projeto
    unzip_control_files(file_path=folder)

    # Segundo, adicionamos pastas vazias dentro da pasta principal
    # mkdir(path=join(folder,'population/configs'))
    # mkdir(path=join(folder,'population/data'))
    # mkdir(path=join(folder,'population/output'))

    # Terceiro, criamos os arquivos variáveis.
    create_geo_cross_walk(project, pop_fldr)

    create_control_totals_taz(project, model_place, pop_fldr)

    create_control_totals_meta(pop_fldr)

    # Quarto, adicionamos os arquivos faltantes nas pastas temporárias do projeto
    # Os arquivos seed_persons e seed_households podem ficar em outras pastas, se necessário.

    # Quinto, executamos o programa
    subprocess.Popen(["python", join(pop_fldr, "run_populationsim.py")], cwd=pop_fldr)

    # Sexto, salvamos as informações das populações sintéticas em databases
    export_syn_pop_data(project, pop_fldr)


def set_thread_number(number: int):
    """
    Set the number of threads to generate the synthetic population. By default, it uses all available threads in the computer.

    """
    if number != 1:
        return mp.cpu_count()
    else:
        return 1


def validate_synthetic_population():

    pass
