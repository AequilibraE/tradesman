from os.path import isdir, join, isfile
from tempfile import gettempdir
from urllib.request import urlretrieve
from zipfile import ZipFile

from tradesman.model_creation.synthetic_population.seeds_url import population_url


def unzip_seed_files(cwd: str):
    """
    Unzips the folder containing the pre-loaded population and household seeds for creating synthetic population.

    Parameters:
        *cwd*(:obj:`str`): current working directory
    """
    if isdir(join(cwd, "population")):
        return

    dest_path = join(gettempdir(), "population.zip")

    if not isfile(dest_path):
        urlretrieve(population_url, dest_path)

    zf = ZipFile(dest_path)

    zf.extractall(cwd)
