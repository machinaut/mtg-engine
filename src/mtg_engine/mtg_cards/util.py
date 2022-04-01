#!/usr/bin/env python
"""
Utility (miscellaneous) functions for mtg_cards.

proxy() converts plain old data from JSON files to a read-only proxy
unproxy() inverts the proxy()
"""


from types import MappingProxyType, NoneType

from IPython import get_ipython


def isnotebook():
    """Return True if we are in a jupyter notebook, else False"""
    # https://stackoverflow.com/a/39662359
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        if shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        return False  # Other type, including NoneType if no ipython
    except NameError:
        return False  # Probably standard Python interpreter


def proxy(data):
    """Get a read-only proxy for a mapping, used for JSON files"""
    if isinstance(data, MappingProxyType):
        return data
    if isinstance(data, dict):
        return MappingProxyType({k: proxy(v) for k, v in data.items()})
    if isinstance(data, list):
        return tuple(proxy(item) for item in data)
    if isinstance(data, (str, int, float, tuple, NoneType)):
        return data
    raise TypeError(f"Unsupported type: {type(data)}")


def unproxy(data):
    """Invert the proxy(), used to save proxy'd data to JSON files"""
    if isinstance(data, MappingProxyType):
        return {k: unproxy(v) for k, v in data.items()}
    if isinstance(data, (tuple, list)):
        return [unproxy(item) for item in data]
    if isinstance(data, (str, int, float, NoneType)):
        return data
    raise TypeError(f"Unsupported type: {type(data)}")
