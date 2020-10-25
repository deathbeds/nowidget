"""interactive traitlets based widgets."""
__version__ = __import__("datetime").date.today().strftime("%Y.%m.%d")


from . import util, base, kernel
from .states import IPYTHON, PYTEST, MAIN
from .base import Trait, Display
from . import template, test
from .template import *


def load_ipython_extension(shell):
    shell.user_ns["shell"] = shell
    base.load_ipython_extension(shell)
    test.load_ipython_extension(shell)
    kernel.load_ipython_extension(shell)


def unload_ipython_extension(shell):
    base.unload_ipython_extension(shell)
    test.unload_ipython_extension(shell)
    kernel.load_ipython_extension(shell)
