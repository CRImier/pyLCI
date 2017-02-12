menu_name = "Nmap"
i = None
o = None

from functools import wraps
import time
import os, sys

from ui import Menu, Printer, format_for_screen as ffs
from if_info import get_ip_addr, get_network_from_ip, sort_ips

try:
    import nmap
except ImportError:
    nmap = None #So we can give an error if nmap module is missing

report_dir = "reports"

#Figuring out where the Python module 
current_module_path = os.path.dirname(sys.modules[__name__].__file__)
if report_dir not in os.listdir(current_module_path):
    os.mkdir(os.path.join(current_module_path, report_dir))

report_dir_full_path = os.path.join(current_module_path, report_dir)

#Global storage variables - can be dumped to a file at any time
current_scan = None
current_filename = ""

def dump_current_scan_to_file():
    if current_scan is not None:
        filename = "{}.xml".format(current_filename)
        filename = filename.replace("/", "-") #For netmasks
        report_path = os.path.join(report_dir_full_path, filename)
        with open(report_path, "w") as f:
            xml = current_scan.get_nmap_last_output()
            f.write(xml)


def save_restore_global_storage(func):
    """A decorator that restores previous contents of report storage 
    once the function that last overwrote it exits."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global current_scan, current_filename
        __current_scan__ = current_scan
        __current_filename__ = current_filename
        result = func(*args, **kwargs)
        current_scan = __current_scan__
        current_filename = __current_filename__
        return result
    return wrapper

#IP/interface/network scanning functions

def scan_localhost(host = "127.0.0.1"):
    scan_ip(host)

def scan_ip(ip, ports="0-1023"):
    Printer("Scanning {}:{}".format(ip, ports), i, o, 0) #Leaves the message on the screen
    nm = nmap.PortScanner()
    nm.scan(ip, ports)
    show_scan_results_for_ip(ip, nm)

def quick_scan_network_by_ip(ip_on_network):
    if ip_on_network == "None":
        Printer("No IP to scan!", i, o, 2)
        return False
    network_ip = get_network_from_ip(ip_on_network)
    Printer("Scanning {}".format(network_ip), i, o, 0)
    nm = nmap.PortScanner()
    nm.scan(network_ip, arguments="-sn")
    show_quick_scan_results_for_network(network_ip, nm)

#Different menus

def scan_network_menu():
    #A report to be passed to Menu object
    networks = []
    #External library function that parses "ip addr" output
    interface_data = get_ip_addr()
    for interface_name in interface_data.keys():
        interface_info = interface_data[interface_name]
        state = interface_info["state"]
        ip = interface_info["addr"] if interface_info["addr"] else "None"
        networks.append( ["{}:{}, {}".format(interface_name, state, ip), lambda x=ip: quick_scan_network_by_ip(x)] )
    Menu(networks, i, o).activate()

def ip_info_menu(ip_info):
    ip = ip_info["addresses"]["ipv4"]
    mac = ip_info["addresses"]["mac"] if "mac" in ip_info["addresses"] else "Unknown MAC"
    vendor = ip_info["vendor"][mac] if mac in ip_info["vendor"] else "Unknown vendor"
    menu_contents = [
    ["IP: {}".format(ip)],
    [mac],
    [vendor],
    ["-Scan ports 0-1023", lambda: scan_ip(ip)]]
    Menu(menu_contents, i, o).activate()
    

#Scan result display functions

@save_restore_global_storage
def show_scan_results_for_ip(ip, ip_results):
    global current_scan, current_filename
    current_scan = ip_results
    current_filename = "ip_{}_{}".format(ip, time.strftime("%Y%m%d-%H%M%S"))
    ip_result = ip_results[ip]
    #Assembling a report we can pass straight to Menu object
    report = []
    #IP, state, hostname
    ip = ip_result["addresses"]["ipv4"]
    report.append([ ["IP: {}, {}".format(ip, ip_result.state())] ])
    report.append([ ["Host: {}".format(ip_result.hostname())] ])
    #Now assemble a list of open ports:
    protocols = ip_result.all_protocols()
    if protocols:
        report.append([["Open ports:"]])
        for protocol in protocols:
            ports = ip_result[protocol]
            for port in ports:
                report.append([["  {}:{}".format(protocol, port)]])
    else: #No open ports for any protocol found?
        report.append([["No open ports found"]])
    #Show report
    Menu(report, i, o).activate()

@save_restore_global_storage
def show_quick_scan_results_for_network(net_ip, net_results):
    global current_scan, current_filename
    current_scan = net_results
    current_filename = "net_{}_{}".format(net_ip, time.strftime("%Y%m%d-%H%M%S"))
    net_report = []
    ips = net_results.all_hosts()
    ips = sort_ips(ips)
    for ip in ips:
        result = net_results[ip]
        print(result)
        mac = result["addresses"]["mac"] if "mac" in result["addresses"] else "Unknown MAC"
        if result["vendor"] and mac in result["vendor"].keys():
            info_str = result["vendor"][mac]
        else:
            info_str = mac
        net_report.append([[ip, info_str], lambda x=result: ip_info_menu(x)])
    Menu(net_report, i, o, entry_height=2).activate()

#pyLCI functions

def callback():
    if nmap is None:
        Printer(ffs("nmap Python module not found!", o.cols), i, o, 3)
        return False
    try:
        nm = nmap.PortScanner()
    except nmap.nmap.PortScannerError:
        Printer(ffs("nmap not installed!", o.cols), i, o, 3)
        return False
    #Dump function support
    i.set_maskable_callback("KEY_F5", dump_current_scan_to_file)
    menu_contents = [
    ["Scan localhost", scan_localhost],
    ["Scan hardcoded IP", lambda: scan_ip("192.168.88.1")],
    ["Scan a network", scan_network_menu]
    ]
    Menu(menu_contents, i, o).activate()
    i.remove_maskable_callback("KEY_F5")

def init_app(input, output):
    global i, o
    i = input; o = output
