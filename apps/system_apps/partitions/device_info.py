#!/usr/bin/env python

import shlex
import os

def get_partitions():
    partitions = []
    labels = {}
    dbu_dir = "/dev/disk/by-uuid/"
    dbl_dir = "/dev/disk/by-label/"
    try:
        parts_by_label = os.listdir(dbl_dir)
    except OSError:
        parts_by_label = [] 
    parts_by_uuid = os.listdir(dbu_dir)
    for label in parts_by_label:
        #Getting the place where symlink points to - that's the needed "/dev/sd**"
        path = os.path.realpath(os.path.join(dbl_dir, label)) 
        if label:
            labels[path] = label
        #Makes dict like {"/dev/sda1":"label1", "/dev/sdc1":"label2"}
    for uuid in parts_by_uuid:
        path = os.path.realpath(os.path.join(dbu_dir, uuid))
        details_dict = {"uuid":uuid, "path":path}
        details_dict["label"] = labels[path] if path in labels else None
        partitions.append(details_dict)
        #partitions is now something like 
        #[{"uuid":"5OUU1DMUCHUNIQUEW0W", "path":"/dev/sda1"}, {"label":"label1", "uuid":"MANYLETTER5SUCH1ONGWOW", "path":"/dev/sdc1"}]
    return partitions

def get_mounted_partitions():
    #Good source of information about mounted partitions is /etc/mtab
    mtab_file = "/etc/mtab" 
    with open(mtab_file, "r") as f:
        lines = f.readlines()
    mounted_partitions = {}
    for line in lines:
        line = line.strip().strip("\n")
        if line: #Empty lines? Well, who knows what happens... =)
            elements = shlex.split(line) #Avoids splitting where space character is enclosed in ###########
            if len(elements) != 6:
                break
            path = elements[0] 
            mountpoint = elements[1] 
            #mtab is full of entries that aren't any kind of partitions we're interested in - that is, physical&logical partitions of disk drives
            #That's why we need to filter entries by path
            if path.startswith("/dev"):
                #Seems to be a legit disk device. It's either /dev/sd** or a symlink to that. If it's a symlink, we resolve it.
                dev_path = os.path.realpath(path)
                mounted_partitions[dev_path] = mountpoint
    return mounted_partitions

if __name__ == "__main__":
    print(get_mounted_partitions())    
    print(scan_partitions())
