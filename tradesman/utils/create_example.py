import zipfile
from pathlib import Path

from aequilibrae.project import Project


def create_example(path: str) -> Project:
    """Copies an example model to a new project project and returns the project handle

    :Arguments:
        **path** (:obj:`str`): Path where to create a new model. Must be a non-existing folder/directory.

    :Returns:
        **project** (:obj:`Project`): AequilibraE Coquimbo Project handle (open)

    """
    pth = Path(path)
    if pth.is_dir() and pth.exists():
        raise FileExistsError("Cannot overwrite an existing directory")

    source = Path(__file__).parent / "reference_files" / "coquimbo.zip"

    pth.mkdir(parents=True, exist_ok=True)
    zipfile.ZipFile(source).extractall(pth)
    return Project.from_path(str(pth))
