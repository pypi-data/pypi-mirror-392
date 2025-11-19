from .trimap_ import TRIMAP

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('trimap')
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["TRIMAP"]
