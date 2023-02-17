import importlib.util as iutil
import os

if iutil.find_spec("shapely"):
    os.environ["USE_PYGEOS"] = "0"

from .model import Tradesman
