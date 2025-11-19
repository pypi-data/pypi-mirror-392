from importlib.metadata import version

from ._core import PythonInfo, whoruv

__all__ = ["whoruv", "PythonInfo"]
__version__ = version("whoruv")  # Python 3.9+ only
