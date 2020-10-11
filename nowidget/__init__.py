"""interactive traitlets based widgets."""
__version__ = "0.1.0"


from . import util, base
from .states import IPYTHON, PYTEST, MAIN
from .base import Trait, Display
from . import template, test
from .template import *


def load_ipython_extension(shell):
    shell.user_ns["shell"] = shell
    base.load_ipython_extension(shell)
    test.load_ipython_extension(shell)


def unload_ipython_extension(shell):
    base.unload_ipython_extension(shell)
    test.unload_ipython_extension(shell)
