#! /usr/bin/python

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import dbus
import dbus.service
import sys
from wicd import misc
misc.RenameProcess('wicd-cli')

if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
    import dbus.glib
else:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

class WicdInterface():
    def __init__(self):
        bus = dbus.SystemBus()
        while True:
            try:
                self.daemon = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon'),
                'org.wicd.daemon')
                self.wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
                'org.wicd.daemon.wireless')
                self.wired = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired'),
                'org.wicd.daemon.wired')
                self.config = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/config'),
                'org.wicd.daemon.config')
            except dbus.DBusException:
                pass
            else:
                print "Successful start"
                break
        if not self.daemon:
            print 'Error connecting to wicd via D-Bus.  Please make sure the wicd service is running.'
            return False

    def get_wireless_interface(self):
        while True:
            try:
	        return self.wireless.DetectWirelessInterface()
            except:
                pass
            else:
                break
        
    def scan(self):
        return self.wireless.Scan(self.get_wireless_interface())
    
    def get_wireless_networks(self):
        network_list = []
        network_number = self.wireless.GetNumberOfNetworks()
        properties = ['essid', 'bssid', 'encryption', 'channel', 'quality', 'mode', 'bitrates', 'encryption_method']
        for number in range(network_number):
            network_list.append({property:str(self.wireless.GetWirelessProperty(number, property)) for property in properties})
        return network_list

    def get_current_network_id(self):
        return self.wireless.GetCurrentNetworkID(0)

    def get_wireless_ip(self):
        return self.wireless.GetWirelessIP(0)

    def disconnect(self):
        return self.daemon.Disconnect()

    def connect(self, network_number):
        self.wireless.ConnectWireless(network_number)

    def check_wireless_connection(self):
        return self.wireless.CheckIfWirelessConnecting()

    def get_connection_status(self):
        return self.wireless.CheckWirelessConnectingStatus()

    def get_connection_message(self):
        return self.wireless.CheckWirelessConnectingStatus()

    
class WicdUserInterface(WicdInterface):

    def __init__(self, screen, listener):
        WicdInterface.__init__(self)
        self.screen = screen
        self.listener = listener

    def choose_networks(self):
        self.scan()
        wireless_networks = self.get_wireless_networks()
        menu_contents = []
        for network in wireless_networks:
            menu_contents.append([network["essid"], lambda: True])
        self.menu = Menu(menu_contents, self.screen, self.listener, "WiFi menu")
        self.menu.activate()        
    
#interface = WicdInterface()
#network_list = interface.get_wireless_networks()
#print network_list
#print "IP is:"+str(interface.get_wireless_ip())
#print "Current network details are: \n"+str(network_list[interface.get_current_network_id()])
#print interface.check_wireless_connection()
#print interface.get_connection_status()
#print interface.get_connection_message()





#print wired.GetWiredProfileList()[0]
#print wired.ReadWiredNetworkProfile(wired.GetWiredProfileList()[0])

"""    num = len(wired.GetWiredProfileList())
    if not (network_id < num and 
            network_id >= 0):
        return False
    else:
        return True

    if not profile_name in wired.GetWiredProfileList():

    elif options.wired:
        if wired.CheckPluggedIn():
            print "Disconnecting from wired connection on %s" % wired.DetectWiredInterface()
    op_performed = True

   elif options.wired:
        print "Connecting to wired connection on %s" % wired.DetectWiredInterface()
        wired.ConnectWired()

        check = lambda: wired.CheckIfWiredConnecting()
        status = lambda: wired.CheckWiredConnectingStatus()
        message = lambda: wired.CheckWiredConnectingMessage()
"""
    # update user on what the daemon is doing


# pretty print optional and required properties
"""def str_properties(prop):
    if len(prop) == 0:
        return "None"
    else:
        return ', '.join("%s (%s)" % (x[0], x[1].replace("_", " ")) for x in type['required'])


if options.wireless and options.list_encryption_types:
    et = misc.LoadEncryptionMethods()
    # print 'Installed encryption templates:'
    print '%s\t%-20s\t%s' % ('#', 'Name', 'Description')
    id = 0
    for type in et:
        print '%s\t%-20s\t%s' % (id, type['type'], type['name'])
        print '  Req: %s' % str_properties(type['required'])
        print '---'
        # don't print optionals (yet)
        #print '  Opt: %s' % str_properties(type['optional'])
        id += 1
    op_performed = True

if options.save and options.network > -1:
    if options.wireless:
        is_valid_wireless_network_id(options.network)
        config.SaveWirelessNetworkProfile(options.network)
    elif options.wired:
        config.SaveWiredNetworkProfile(options.name)
    op_performed = True


"""
