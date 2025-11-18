from importlib.metadata import version

from ._core import VersionInfo, bumpuvError, update_version

__all__ = ["update_version", "VersionInfo", "bumpuvError"]


__version__ = version("bumpuv")  # Python 3.9+ only
