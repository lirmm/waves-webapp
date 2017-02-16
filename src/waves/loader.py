import importlib
import pkgutil
from inspect import getmembers, isabstract, isclass
from waves_adaptors.core.base import JobAdaptor, AdaptorImporter

__all__ = ['load_extra_adaptors']


def isAdaptorClass(value):
    return not isabstract(value) and isclass(value)


def load_core():
    return sorted(__load_addons('waves_adaptors.core', parent=JobAdaptor), key=lambda x: x[0])


def load_extra_adaptors():
    return sorted(__load_addons('waves_addons.adaptors', parent=JobAdaptor), key=lambda x: x[0])


def load_extra_importers():
    return sorted(__load_addons('waves_addons.importers', parent=AdaptorImporter), key=lambda x: x[0])


def __load_addons(path, parent):
    submodules = __import_submodules(path, True)
    adaptors = []
    for submodule_name, submodule in submodules.items():
        adaptors.extend([mem for mem in getmembers(submodule, isAdaptorClass)
                         if mem[1].__module__ == submodule.__name__ and issubclass(mem[1], parent)])
    return adaptors


def __import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(__import_submodules(full_name))
    return results
