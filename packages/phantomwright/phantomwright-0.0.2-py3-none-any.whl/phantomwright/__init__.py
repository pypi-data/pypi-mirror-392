import patchright

from patchright import *

try:
    __all__ = patchright.__all__
except AttributeError:
    __all__ = [name for name in dir(patchright) if not name.startswith("_")]
