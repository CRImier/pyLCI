#!/usr/bin/env python
import sys
from subprocess import Popen
from time import sleep

#Using I2C = apt-get python-smbus i2cdetect
##Using serial - python-serial
#Using pifacecad - pip pifacecad
#Using HID - python evdev
#Using GPIO - RPi.GPIO


#Translation of choices to apt-get and pip modules which need to be installed
#Choice names shouldn't be the same in different modules!
preassembled_modules ={
'pifacecad':{'apt-get':['python-pifacecad']}
}

separate_modules ={
'serial':{'apt-get':['python-serial']},
'i2c':{'apt-get':['python-smbus', 'i2c-tools']},
'hid':{'apt-get':['python-dev'], 'pip':['evdev']},
'rpi_gpio':{'apt-get':['python-rpi.gpio']}
}
#Radio menu translations:
preassembled_module_names ={
"PiFaceCAD":'pifacecad'
}

def call_interactive(command):
    p = Popen(command, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
    while p.poll() is None:
        try:
            sleep(1)
        except KeyboardInterrupt:
            p.terminate()
            break


def yes_or_no(string, default=False):
    while True:
        answer = raw_input(string+" ").lower() #Adding whitespace for prompt to look better
        if answer == "":
            return default
        elif answer.startswith('y'):
            return True
        elif answer.startswith('n'):
            return False
        else:
            pass #Looping until a comprehensible answer is given

def radio_choice(strings, prompt="Choose one:"):
    while True:
        for index, string in enumerate(strings):
            print "{} - {}".format(index, string)
        choice_str = raw_input(prompt+" ")
        try:
            choice = int(choice_str)
        except ValueError:
            print("Choice should be an integer")
        else:
            break
    return choice

print("Hello! I'm glad that you've chosen pyLCI")
print("Let me help you out with installing necessary Python modules and utilities.")
print("Feel free to restart this script if you screwed up")

options = []

if yes_or_no("Do you use any of pre-assembled I/O modules, such as PiFaceCAD (the only supported right now)?"):
   pretty_names = preassembled_module_names.keys()
   answer = radio_choice(pretty_names)
   module_pname = pretty_names[answer]
   module_name = preassembled_module_names[module_pname]
   options.append(module_name)
if yes_or_no("Do you connect any of your I/O devices by I2C?"):
   options.append('i2c')
if yes_or_no("Do you connect any of your I/O devices by serial, either hardware or serial over USB?"):
   options.append('serial')
if yes_or_no("Do you use HID devices, such as keyboards and keypads?"):
   options.append('hid')
if yes_or_no("Do you use Raspberry Pi GPIO port devices (not I2C or SPI)?"):
   options.append('rpi_gpio')

#Joining both module dictionaries for convenience
both_dicts = {}
both_dicts.update(preassembled_modules)
both_dicts.update(separate_modules)

apt_get = []
pip = []
for option in options:
   option_desc = both_dicts[option]
   apt_get_packages = option_desc['apt-get'] if 'apt-get' in option_desc else []
   pip_modules = option_desc['pip'] if 'pip' in option_desc else []
   for package in apt_get_packages:
       apt_get.append(package)
   for module in pip_modules:
       pip.append(module)

print(apt_get)
print(pip)

if apt_get:
    call_interactive(['apt-get', 'update'])
    call_interactive(['apt-get', '--ignore-missing', 'install'] + apt_get)

if pip:
    call_interactive(['pip', 'install'] + apt_get)

