import os
subdirs = [x[0] for x in os.walk('./apps')]
storage_dirs = []

def get_storage_dirs(dir, dir_list):
    for directory in [os.path.join(dir, entry) for entry in os.listdir(dir) if os.path.isdir(os.path.join(dir, entry))]:
        contents = os.listdir(directory)
        if "__init__.py" in contents and "main.py" not in contents:
            dir_list.append(directory)
            get_storage_dirs(directory, dir_list)

storage_dirs.append('./apps')
get_storage_dirs("./apps", storage_dirs)
module_dirs = []

storage_with_modules = {}

for storage_dir in storage_dirs:
    #contents = [os.path.join(storage_dir, entry) for entry in os.listdir(storage_dir)]
    contents = [os.path.join(storage_dir, entry) for entry in os.listdir(storage_dir)]
    subdirs = [entry for entry in contents if os.path.isdir(entry)]
    for module_dir in [subdir for subdir in subdirs if subdir not in storage_dirs]:
        module_dirs.append(module_dir)

non_loadable = [module for module in module_dirs if "do_not_load" in os.listdir(module)]
module_paths = [os.path.relpath(module, "./apps") for module in module_dirs if module not in non_loadable]
module_import_paths = [path.replace('/', '.') for path in module_paths]
module_list = zip(module_paths, module_import_paths)
#module_dict = dict(zip(module_paths, module_import_paths))
#print(module_dict)
