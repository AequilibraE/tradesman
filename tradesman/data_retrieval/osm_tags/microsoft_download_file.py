from tempfile import gettempdir
import zipfile
from os.path import join, isfile, dirname
from urllib.request import urlretrieve
import pandas as pd
import pycountry


def microsoft_download_file(model_place: str):
    """
    Download file containing Microsoft Bing buildings, and unzip it.

    Parameters:
         *model_palce*(:obj:`str`): current model place
    """

    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    df = pd.read_csv(join(dirname(__file__), "data/microsoft_countries_and_territories.csv"))

    if country_code in df.iso_code.values:
        url = df[df.iso_code == country_code].url.values[0]
    else:
        raise FileNotFoundError("Microsoft Bing does not provide information about this region.")

    dest_path = join(gettempdir(), f"{country_code}_bing.zip")

    if not isfile(dest_path):
        urlretrieve(url, dest_path)

    zf = zipfile.ZipFile(dest_path)

    zf.extractall(gettempdir())
