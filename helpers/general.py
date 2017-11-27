import os
import sys

def local_path_gen(_name_):
    """This function generates a ``local_path`` function you can use
    in your scripts to get an absolute path to a file in your app's 
    directory. You need to pass ``__name__`` to ``local_path_gen``. Example usage:
    
    .. code-block:: python

        from helpers import local_path_gen
        local_path = local_path_gen(__name__)
        ...
        config_path = local_path("config.json")
    
    The resulting local_path function supports multiple arguments, 
    passing all of them to ``os.path.join`` internally."""
    app_path = os.path.dirname(sys.modules[_name_].__file__)
    def local_path(*path):
        return os.path.join(app_path, *path)
    return local_path
