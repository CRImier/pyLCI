menu_name = "Wireless"
#Some globals for LCS
callback = None
#Some globals for us
main_menu = None
i = None
o = None

from time import sleep

from ui.menu import Menu

import wpa_cli

def show_networks():
    network_menu_contents = []
    networks = wpa_cli.get_scan_results()
    for network in networks:
        network_menu_contents.append([network['ssid'], lambda x=network: network_info_menu(x)])
    network_menu_contents.append(["Exit", 'exit'])
    network_menu = Menu(network_menu_contents, o, i, "Wireless network menu")
    network_menu.activate()

def network_info_menu(network_info):
    network_info_contents = [
    ["Connect", lambda x=network_info: connect_to_network(x)],
    #["BSSID", lambda x=network_info['bssid']: print_to_display(x, sleep_time=5)],
    #["Frequency", lambda x=network_info['frequency']: print_to_display(x, sleep_time=5)],
    #["Open" if wpa_cli.is_open_network(network_info) else "Secured", lambda x=network_info['flags']: print_to_display(x, sleep_time=5)],
    ["Open" if wpa_cli.is_open_network(network_info) else "Secured"],
    ["Exit", 'exit']]
    network_info_menu = Menu(network_info_contents, o, i, "Wireless network info")
    network_info_menu.activate()

"""    
def print_to_display(value, sleep_time=1):
    o.display_data(value[:o.cols], value[o.cols:][o.cols])
    sleep(sleep_time)
"""

def connect_to_network(network_info):
    #First, looking in the known networks
    configured_networks = wpa_cli.list_configured_networks()
    for network in configured_networks:
        if network_info['ssid'] == network['ssid']:
            o.display_data(network_info['ssid'], "already set up")
            wpa_cli.select_network(network['network id'])
            return True
    #Then, if it's an open network, just connecting
    if wpa_cli.is_open_network(network_info):
        network_id = wpa_cli.add_network()
        o.display_data("Network is open", "adding to known")
        wpa_cli.set_network(network_id, 'ssid', '"'+network_info['ssid']+'"')
        wpa_cli.set_network(network_id, 'key_mgmt', 'NONE')
        o.display_data("Connecting to", network_info['ssid'])
        wpa_cli.select_network(network_id)
        return True
    #No passkey/WPS PIN input possible yet and I cannot yet test WPS button functionality.
    else:
        o.display_data("Network password", "unknown")
        sleep(1)
        return False

def scan():
    try:
        wpa_cli.initiate_scan()
    except wpa_cli.WPAException as e:
        if e.code=="FAIL-BUSY":
            o.display_data("Still scanning...")
        else:
            raise
    else:
        o.display_data("Scanning...")
    finally:
        sleep(1)

def wireless_status():
    w_status = wpa_cli.connection_status()
    state = w_status['wpa_state']
    status_menu_contents = [[["state:", state]]] #State is an element that's always there, let's see possible states
    if state == 'COMPLETED':
        #We have bssid, ssid and key_mgmt at least
        status_menu_contents.append(['SSID: '+w_status['ssid']])
        status_menu_contents.append(['BSSID: '+w_status['bssid']])
        key_mgmt = w_status['key_mgmt']
        status_menu_contents.append([['Security:', key_mgmt]])
        #If we have WPA in key_mgmt, we also have pairwise_cipher and group_cipher set to something other than NONE so we can show them
        if key_mgmt != 'NONE':
            group = w_status['group_cipher']
            pairwise = w_status['pairwise_cipher']
            status_menu_contents.append([['Group/Pairwise:', group+"/"+pairwise]])
    elif state in ['AUTHENTICATING', 'SCANNING', 'ASSOCIATING']:
        pass #These states don't have much information
    #In any case, we might or might not have IP address info
    status_menu_contents.append([['IP address:',w_status['ip_address'] if 'ip_address' in w_status else 'None']])
    #We also always have WiFi MAC address as 'address'
    status_menu_contents.append(['MAC: '+w_status['address']])
    status_menu = Menu(status_menu_contents, o, i, "Wireless status menu", entry_height=2)
    status_menu.activate()

def change_interface():
    #This function builds a menu out of all the interface names, each having a callback to show_if_function with interface name as argument
    menu_contents = []
    interfaces = wpa_cli.get_interfaces()
    for interface in interfaces:
        menu_contents.append([interface, lambda x=interface: change_current_interface(x)])
    menu_contents.append(["Exit", 'exit'])
    interface_menu = Menu(menu_contents, o, i, "Interface change menu")
    interface_menu.activate()

def change_current_interface(interface):
    try:
        wpa_cli.set_active_interface(interface)
    except wpa_cli.WPAException:
        o.display_data('Failed to change', 'interface')
    else:
        o.display_data('Changed to', interface)
    finally:
        sleep(1) #Leave some time to see the message
        
def init_app(input, output):
    global callback, main_menu, i, o
    main_menu_contents = [
    [wpa_cli.get_current_interface(), change_interface],
    ["Scan", scan],
    ["Networks", show_networks],
    ["Status", wireless_status],
    #["Saved networks", manage_saved_networks],
    ["Exit", 'exit']]
    i = input; o = output
    main_menu = Menu(main_menu_contents, o, i, "wpa_cli main menu")
    callback = main_menu.activate
    

#main_menu.activate = activate_wrapper(main_menu.activate)

"""def activate_wrapper(activate_cb):
    def wrapper():
        update_if_menu_contents()
        try:
            activate_cb()
        except wpa_cli
            wpa_cli.()
    return wrapper"""

