import subprocess
#Description used for all interfaces
from copy import copy

if_description = { 
   'state':'down',
   'addr':None,
   'addr6':None,
   'ph_addr':None    
}

def parse_params(param_string):
    state = None
    words = param_string.split(" ")
    for index, word in enumerate(words):
        if word == 'state':
            state = words[index+1].lower()
    return {'state':state}

def parse_ip_addr():
    interfaces = {}
    current_if = None
    ip_output = subprocess.check_output(['ip', 'addr'])
    ip_output = [line for line in ip_output.split('\n') if line != ""]
    for line in ip_output:
        if line[0].isdigit(): #First line for interface
            num, if_name, params = line.split(':', 2)
            if_name = if_name.strip(" ")
            current_if = if_name
            interfaces[if_name] = copy(if_description)
            param_dict = parse_params(params)
            interfaces[if_name].update(param_dict)
        else: #Lines that continue describing interfaces
            line = line.lstrip()
            if line.startswith('inet '):
                words = line.split(" ")
                interfaces[current_if]['addr'] = words[1]
            if line.startswith('link/ether'):
                words = line.split(" ")
                interfaces[current_if]['ph_addr'] = words[1]
            if line.startswith('inet6'):
                words = line.split(" ")
                interfaces[current_if]['addr6'] = words[1]
    return interfaces

if __name__ == "__main__":
    print(parse_ip_addr())
