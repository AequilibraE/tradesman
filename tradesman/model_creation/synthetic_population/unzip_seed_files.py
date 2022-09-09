from tempfile import gettempdir
import requests
from zipfile import ZipFile
from io import BytesIO
from os.path import isdir, join, isfile
from urllib.request import urlretrieve
from tradesman.model_creation.synthetic_population.seeds_url import population_url


def unzip_seed_files(cwd: str):
    """
    This function unzips the folder containg the pre-loaded popoulation and household seeds for creating synthetic population.
    Args.:
        *cwd*(:obj:`str`): current working directory
    """
    if isdir(join(cwd, "population")):
        return

    dest_path = join(gettempdir(), "population.zip")

    if not isfile(dest_path):
        urlretrieve(population_url, dest_path)

    zf = ZipFile(dest_path)

    zf.extractall(cwd)
