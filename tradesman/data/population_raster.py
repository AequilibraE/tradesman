import urllib.request
from os.path import isfile, join
from tempfile import gettempdir

import numpy as np
import pandas as pd
from aequilibrae import Project
from scipy.sparse import coo_matrix
from tradesman.data.mask_raster import mask_raster

from tradesman.data_retrieval.country_main_area import model_borders
from tradesman.utils.tqdm_download import TqdmUpTo


def population_raster(data_link: str, field_name: str, project: Project):
    """
    Reads the population raster.

    Parameters:
        *data_link*(:obj:`str`): URL link to download the file
        *field_name*(:obj:`str`): desired filed name
        *project*(:obj:`aequilibrae.project`): currently open project
    """
    dest_path = join(gettempdir(), f"{field_name}.tif")
    if not isfile(dest_path):
        with TqdmUpTo(unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{field_name}.tif") as t:
            urllib.request.urlretrieve(data_link, filename=dest_path, reporthook=t.update_to, data=None)
            t.total = t.n
    main_area = model_borders(project)

    dataset = mask_raster(dest_path, main_area)

    minx, miny, maxx, maxy = main_area.bounds
    width = dataset.width
    height = dataset.height
    x_min = dataset.bounds.left
    y_max = dataset.bounds.top
    x_size, y_size = dataset.res

    # Computes the X and Y indices for the XY grid that will represent our raster
    y_idx = []
    for row in range(height):
        y = row * (-y_size) + y_max + (y_size / 2)  # to centre the point
        y_idx.append(y)
    y_idx = np.array(y_idx)

    x_idx = []
    for col in range(width):
        x = col * x_size + x_min + (x_size / 2)  # add half the cell size
        x_idx.append(x)
    x_idx = np.array(x_idx)

    # Read the data and build the population dataset
    data = dataset.read(1)
    mat = coo_matrix(data)
    rows = y_idx[mat.row]
    cols = x_idx[mat.col]
    df = pd.DataFrame({"longitude": cols, "latitude": rows, "population": mat.data})
    df = df.loc[df.population >= 0, :]  # Pixels outside the modeled area have negative values
    df = df[(df.longitude > minx) & (df.longitude < maxx) & (df.latitude > miny) & (df.latitude < maxy)]
    df.fillna(0, inplace=True)

    return df
