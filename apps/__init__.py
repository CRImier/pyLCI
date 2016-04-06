import os

def is_module_dir(dir_path):
    contents = os.listdir(dir_path)
    if "main.py" in contents:
        return True
    else:
        return False
    
def is_subdir(dir_path):
    contents = os.listdir(dir_path)
    if "__init__.py" in contents and "main.py" not in contents:
        return True
    else:
        return False
    

def app_walk(base_dir):
    walk_results = []
    modules = []
    subdirs = []
    for element in os.listdir(base_dir):
        full_path = os.path.join(base_dir,element)
        if os.path.isdir(full_path):
            if is_subdir(full_path):
                subdirs.append(element)
                results = app_walk(full_path)
                for result in results:
                    walk_results.append(result)
            elif is_module_dir(full_path):
                modules.append(element)
    walk_results.append((base_dir, subdirs, modules))
    return walk_results



#for entry in app_walk("./apps"):
#    print(entry)




"""

def get_storage_dirs(dir, dir_list):
    for directory in [os.path.join(dir, entry) for entry in os.listdir(dir) if os.path.isdir(os.path.join(dir, entry))]:
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



"""
