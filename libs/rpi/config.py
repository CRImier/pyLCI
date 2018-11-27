from copy import copy

def is_comment_line(line):
    return line.strip().startswith('#')

def may_be_param_line(line):
    return "=" in line

def read_config(path = "/boot/config.txt"):
    with open(path, "r") as f:
        return f.read()

def write_config(output, path = "/boot/config.txt"):
    with open(path, "w") as f:
        return f.write(output)

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

def is_commented_out(entry):
    if isinstance(entry, dict):
        return is_comment_line(entry["prefix"])
    elif isinstance(entry, basestring):
        return is_comment_line(entry)
    else:
        raise ValueError("Wrong entry supplied: {}".format(entry))

def entry_position(key, value, entries):
    for i, entry in enumerate(entries):
        if isinstance(entry, dict):
            if entry["key"] == key:
                if entry["value"] == value:
                    return i
    return None

def add_entry(key, value, entries, commented_out=False, postfix=" # Auto-inserted"):
    suitable_pos = len(entries)-1
    while entries[suitable_pos]:
        suitable_pos -= 1
    prefix = '#' if commented_out else ''
    entries.insert(suitable_pos, {"prefix":prefix, "key":key, "value":value, "postfix":postfix})
    return True

def remove_entry(key, value, entries):
    position = entry_position(key, value, entries)
    if not position:
        return False
    else:
        entries.pop(position)
        return True

def make_sure_is_present(key, value, entries, reason=None):
    position = entry_position(key, value, entries)
    if not position:
        add_entry(key, value, entries, postfix=reason)
        return True
    return False

def make_sure_is_uncommented(key, value, entries, reason=None):
    position = entry_position(key, value, entries)
    if not position:
        if reason: reason = " # "+reason
        add_entry(key, value, entries, postfix=reason)
        return True
    else:
        entry = entries[position]
        if is_commented_out(entry):
            entry["prefix"] = ''
            if reason:
                entry["postfix"] = " # "+reason
            return True
        return False

def make_sure_is_commented_out(key, value, entries, reason=None):
    position = entry_position(key, value, entries)
    if not position:
        if reason: reason = " # "+reason
        add_entry(key, value, entries, commented_out=True, postfix=reason)
        return True
    else:
        entry = entries[position]
        if not is_commented_out(entry):
            entry["prefix"] = '#'
            if reason:
                entry["postfix"] = " # "+reason
            return True
        return False


if __name__ == "__main__":
    entries = get_config()
    make_sure_is_commented_out("dtoverlay", "sdio,poll_once=off", entries, reason="Auto-commented out by Fix WiFi app")
    make_sure_is_uncommented("dtoverlay", "pi3-miniuart-bt", entries, reason="Auto-uncommented by Fix WiFi app")
    print(recreate_config(entries))
