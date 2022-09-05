from signal import raise_signal
import requests
from zipfile import ZipFile
from io import BytesIO
from os.path import isdir, join
from urllib.request import urlopen


def unzip_seed_files(url: str, cwd: str):
    """
    This function unzips the folder containg the pre-loaded popoulation and household seeds for creating synthetic population.
    Args.:
        *cwd*(:obj:`str`): current working directory
    """
    if isdir(join(cwd, "population")):
        return

    # url = "https://github.com/AequilibraE/tradesman/releases/download/V0.1b/population.zip"

    if urlopen(url).code == 200:

        req = requests.get(url)

        zf = ZipFile(BytesIO(req.content))

        zf.extractall(cwd)
    else:
        raise FileNotFoundError("The provided url presents no zip file.")
