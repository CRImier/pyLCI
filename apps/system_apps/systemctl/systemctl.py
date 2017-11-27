import subprocess


def list_units():
    units = []
    output = subprocess.check_output(["systemctl", "list-units", "-a"])
    lines = output.split('\n')[1:][:-8]
    for line in lines:
        line = ' '.join(line.split()).strip(' ') #Removing all redundant whitespace
        if line.startswith('\xe2\x97\x8f'): #Special character that is used by systemctl output to mark units that failed to load
            elements = line.split(' ', 5)[1:] #Omitting that first element since it doesn't convey any meaning
        else:
            elements = line.split(' ', 4)
        if len(elements) == 5:
            name, loaded, active, details, description = elements
            basename, type = name.rsplit('.', 1)
            name = name.replace('\\x2d', '-') #Replacing unicode dashes with normal ones
            units.append({"name":name, "load":loaded, "active":active, "sub":details, "description":description, "type":type, "basename":basename})
        else:
            print("Systemctl: couldn't parse line: {}".format(repr(line)))
    return units         
                     
def action_unit(action, unit):
    try:
        output = subprocess.check_output(["systemctl", action, unit])
        return True
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    units = list_units()
    
    loadeds = []
    actives = []
    subs = []
    for unit in units:
        loadeds.append(unit["load"])
        actives.append(unit["active"])
        subs.append(unit["sub"])
    print(set(loadeds))
    print(set(actives))
    print(set(subs))
    #for unit in units:
    #    if unit["type"] == 'service' and unit['sub'] =='running' :
    #        print(unit["basename"])
    #print([unit for unit in units if unit["type"] == 'service'])
    #print([unit for unit in units if unit["name"].endswith('.service')])
    #endings = []
    #for unit in units:
    #    name =  unit["name"]
    #    ending = name.rsplit('.')[-1:][0]
    #    endings.append(ending)
    #print(set(endings))
