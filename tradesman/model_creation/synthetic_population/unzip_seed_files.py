import requests
from zipfile import ZipFile
from io import BytesIO
from os.path import isdir, join

from tradesman.model_creation.synthetic_population.seeds_url import population_url

def unzip_seed_files(url:str, cwd: str):
    """
    This function unzips the folder containg the pre-loaded popoulation and household seeds for creating synthetic population.
    Args.:
        *cwd*(:obj:`str`): current working directory
    """
    if isdir(join(cwd, "population")):
        return

    # url = "https://github.com/AequilibraE/tradesman/releases/download/V0.1b/population.zip"

    req = requests.get(url)

    if req.status_code == requests.codes.ok:

        zf = ZipFile(BytesIO(req.content))

        zf.extractall(cwd)
