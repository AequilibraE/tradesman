import requests
import zipfile
from io import BytesIO


def unzip_control_and_seed_files(file_path: str):

    url = "https://github.com/AequilibraE/tradesman/releases/download/V0.1b/population.zip"

    req = requests.get(url)

    zf = zipfile.ZipFile(BytesIO(req.content))

    zf.extractall(file_path)
