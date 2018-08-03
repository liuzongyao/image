import importlib
import types
from common.exceptions import NotFoundError


def get_imported_module_from_file(file_name, package):
    """ import module from python file path and return imported module
    """
    imported_module = importlib.import_module(file_name, package=package)
    importlib.reload(imported_module)

    return imported_module


def filter_module(module, filter_type):
    """ filter variables from import module
    @params
        module: imported module
        filter_type: "variable"
    """
    filter_type = is_variable
    module_functions_dict = dict(filter(filter_type, vars(module).items()))
    return module_functions_dict


def is_variable(tup):
    """ Takes (name, object) tuple, returns True if it is a variable.
    """
    name, item = tup
    if callable(item):
        # function or class
        return False

    if isinstance(item, types.ModuleType):
        # imported module
        return False

    if name.startswith("_"):
        # private property
        return False

    return True


def search_conf_item(item_type, item_name, file_name='.settings', package='common'):
    """ search expected function or variable recursive upward
    @param
        item_type: "variable"
        item_name: variable name
    """
    imported_module = get_imported_module_from_file(file_name, package)
    items_dict = filter_module(imported_module, item_type)
    if item_name in items_dict:
        return items_dict[item_name]
    else:
        raise NotFoundError("{} not found in file {}".format(item_name, file_name))