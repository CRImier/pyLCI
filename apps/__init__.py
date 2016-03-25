import os
subdirs = [x[0] for x in os.walk('./apps')]
module_dirs = [subdir for subdir in subdirs if "main.py" in os.listdir(subdir)]
non_loadable = [module for module in module_dirs if "do_not_load" in os.listdir(module)]
module_names = [os.path.split(module)[1] for module in module_dirs if module not in non_loadable]
