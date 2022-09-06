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

    if urlopen(url).code == 200: #if not isfile(join(gettempdir(), "population.zip")):

        req = requests.get(url)

        zf = ZipFile(BytesIO(req.content))

        zf.extractall(cwd)
    else:
        raise FileNotFoundError("The provided url presents no zip file.")

    # Um teste que verifica se o url funciona (existe)
    # Assumindo que o url existe, faz um download do zip pro temp_folder, e dá o extract fora do zip.
    # Coloca o zip de teste no temp folder.
    # O que vc não tá testando é se faz o download.