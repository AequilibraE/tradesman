import requests
import zipfile
from io import BytesIO


def unzip_control_and_seed_files(cwd: str):
    """
    This function unzips the folder containg the pre-loaded popoulation and household seeds for creating synthetic population.
    Args.:
         *cwd*(:obj:`str`): current working directory
    """

    url = "https://github.com/AequilibraE/tradesman/releases/download/V0.1b/population.zip"

    req = requests.get(url)

    zf = zipfile.ZipFile(BytesIO(req.content))

    zf.extractall(cwd)
