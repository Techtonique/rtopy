"""Top-level package for rtopy."""

__author__ = """T. Moudiki"""
__email__ = "thierry.moudiki@gmail.com"

"""rtopy: Lightweight R-Python bridge."""
from .rtopy import callfunc
from .bridge import RBridge, call_r
from .exceptions import RExecutionError, RNotFoundError, RTypeError

__version__ = "0.2.0"
__all__ = [
    "RBridge",
    "call_r",
    "callfunc",
    "RExecutionError",
    "RNotFoundError",
    "RTypeError",
    "__version__",
]
