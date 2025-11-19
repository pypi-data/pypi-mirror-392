# timesat/__init__.py
from ._timesat import *   # expose all Fortran functions
__version__ = "4.1.10"
__all__ = [name for name in dir() if not name.startswith("_")]