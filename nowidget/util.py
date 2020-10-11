import sys
import abc
import inspect


def istype(object, cls):
    return isinstance(object, type) and issubclass(object, cls)


def minify(x):
    """minify html"""
    return __import__('htmlmin').minify(
        x, False, True, True, True, True, True, True)


def encode(object):
    if isinstance(object, bytes):
        object = __import__('base64').b64encode(object).decode('utf-8')
    return object


def iswidget(object):
    if 'ipywidgets' in sys.modules:
        if isinstance(object, __import__('ipywidgets').Widget):
            return True
    return False


def ispanel(object):
    if 'param' in sys.modules:
        if isinstance(object, __import__('param').Parameterized):
            return True
    return False


def isinteractive(object):
    return iswidget(object) | ispanel(object)


def get_caller_namespace():
    frame = inspect.currentframe()
    while frame.f_locals is not frame.f_globals:
        frame = frame.f_back
    return frame.f_globals


def in_pytest():
    import sys
    import inspect
    import pathlib
    if '_pytest' not in sys.modules:
        return False
    import _pytest
    prefix = pathlib.Path(_pytest.__file__).parent.__str__()
    frame = inspect.currentframe()
    while True:
        if '__file__' in frame.f_globals:
            if frame.f_globals['__file__'].startswith(prefix):
                return True
        if not frame.f_back:
            return False
        frame = frame.f_back
    return False


def active_types(shell=None):
    """get the active types in the current IPython shell.

    we ignore latex, but i forget why."""
    import IPython
    shell = shell or IPython.get_ipython()
    if shell:
        object = list(shell.display_formatter.active_types)
        object.insert(object.index('text/html'),
                      object.pop(object.index('text/latex')))
        return reversed(object)
    return []
