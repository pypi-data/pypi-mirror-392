try:
    from .__version__ import __version__, __version_tuple__, version, version_tuple
except ImportError:
    __version__ = version = None
    __version_tuple__ = version_tuple = ()

from .dataset import Dataset
from .drivers import Drivers, to_geopandas, to_pyvista
from .objects import Chunk, Geometry, Grid, Mesh, Well, decode

find = Dataset.find
load = Dataset.load
read = Dataset.read


def getCapabilities():
    return list(Geometry.names)


def getWrappers():
    return list(Drivers.keys())
