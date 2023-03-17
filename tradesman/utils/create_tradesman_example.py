from os.path import join, dirname, isdir
from os import makedirs
import zipfile
from aequilibrae.project import Project


def create_tradesman_example(path: str):
    """
    Opens a built-in example of a Tradesman model for Nauru.
    Based on AequilibraE's create_example function.

    Parameters:
        *path*(:obj:`str`): path to example folder.
    """

    if isdir(path):
        raise FileExistsError("Cannot overwrite an existing directory")

    makedirs(path, exist_ok=True)
    zipfile.ZipFile(join(dirname(__file__), "../reference_files/nauru.zip")).extractall(path)
    proj = Project()
    proj.open(path)
    return proj
