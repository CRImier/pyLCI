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
