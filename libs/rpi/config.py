from copy import copy

def is_comment_line(line):
    return line.strip().startswith('#')

def may_be_param_line(line):
    return "=" in line

def read_config(path = "/boot/config.txt"):
    with open(path, "r") as f:
        return f.read()

def parse_output(output):
    #Preserving file structure as much as possible
    entries = []
    entry_skeleton = {"prefix":'', "key":'', "value":'', "postfix":''}
    for line in output.split("\n"):
        if not line.strip():
            # Empty line
            entries.append(line)
        elif may_be_param_line(line):
            entry = copy(entry_skeleton)
            # Parameter?
            # Might be a parameter but commented out
            while line.startswith(' ') or line.startswith('#'):
                entry["prefix"] += line[0]
                line = line[1:]
            entry["key"], val_and_psfx = line.split('=', 1)
            while val_and_psfx and not val_and_psfx.startswith(' ') and not val_and_psfx.startswith('#'):
                print(val_and_psfx)
                entry["value"] += val_and_psfx[0]
                val_and_psfx = val_and_psfx[1:]
            entry["postfix"] = val_and_psfx
            entries.append(entry)
        else: #whatever that is
            entries.append(line)
    return entries

def get_config():
    return parse_output(read_config())

def recreate_config(entries):
    lines = []
    for entry in entries:
        if isinstance(entry, basestring):
            lines.append(entry)
        elif isinstance(entry, dict):
            line = "".join([entry["prefix"], entry["key"], '=', entry["value"], entry["postfix"]])
            lines.append(line)
        else:
            raise ValueError("Wrong entry supplied: {}".format(entry))
    return "\n".join(lines)

if __name__ == "__main__":
    print(recreate_config(get_config()))
