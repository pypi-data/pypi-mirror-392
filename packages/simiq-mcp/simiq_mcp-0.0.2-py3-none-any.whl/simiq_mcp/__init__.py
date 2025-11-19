
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("chipiq-mcp")
except PackageNotFoundError:
    __version__ = "-.-.-"
