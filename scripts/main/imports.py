import importlib


def class_import(path):
    path_module, path_class = path.rsplit('.')
    module = importlib.import_module(path_module)
    return getattr(module, path_class)
