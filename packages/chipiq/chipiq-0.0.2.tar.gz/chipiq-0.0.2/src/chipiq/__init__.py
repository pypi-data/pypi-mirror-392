
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("chipiq")
except PackageNotFoundError:
    __version__ = "-.-.-"
