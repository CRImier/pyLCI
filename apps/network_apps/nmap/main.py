menu_name = "Nmap"
i = None
o = None

from time import sleep

from ui import Menu, Printer
from if_info import get_ip_addr, get_network_from_ip, sort_ips



try:
    import nmap
except ImportError:
    nmap = None

try:
    import ipaddr
except ImportError:
    ipaddr = None

def scan_localhost(host = "127.0.0.1"):
    scan_ip(host)

def scan_ip(ip, ports="0-1023"):
    Printer("Scanning {}:{}".format(ip, ports), i, o, 0) #Leaves the message on the screen
    nm = nmap.PortScanner()
    nm.scan(ip, ports)
    #Scan results for the IP, as we get them from nmap interface
    ip_results = nm[ip]
    show_scan_results_for_ip(ip_results)

def scan_network_menu():
    #First, if external ipaddr library is not accessible, there's nothing to do here
    if ipaddr is None:
        Printer(ffs("ipaddr Python module not found!", o.cols), i, o, 3)
        return False
    #A report to be passed to Menu object
    networks = []
    #External library function that parses "ip addr" output
    network_info = get_ip_addr()
    for interface_name in network_info.keys():
        interface_info = network_info[interface_name]
        state = interface_info["state"]
        ip = interface_info["addr"] if interface_info["addr"] else "None"
        networks.append( ["{}:{}, {}".format(interface_name, state, ip), lambda x=ip: quick_scan_network_by_ip(x)] )
    Menu(networks, i, o).activate()

def quick_scan_network_by_ip(ip_on_network):
    ip_report = []
    if ip_on_network == "None":
        Printer("No IP to scan!", i, o, 2)
        return False
    network_ip = get_network_from_ip(ip_on_network)
    Printer("Scanning {}".format(network_ip), i, o, 0)
    nm = nmap.PortScanner()
    nm.scan(network_ip, arguments="-sn")
    ips = nm.all_hosts()
    ips = sort_ips(ips)
    for ip in ips:
        if ip == ip_on_network.split('/')[0]:
            continue
        result = nm[ip]
        print(result)
        ip_report.append([[result["addresses"]["ipv4"], result["addresses"]["mac"]], lambda x=ip: scan_ip(x)])
    Menu(ip_report, i, o, entry_height=2).activate()

def show_scan_results_for_ip(ip_results):
    #Assembling a report we can pass straight to Menu object
    report = []
    #IP, state, hostname
    ip = ip_results["addresses"]["ipv4"]
    report.append([ ["IP: {}, {}".format(ip, ip_results.state())] ])
    report.append([ ["Host: {}".format(ip_results.hostname())] ])
    #Now assemble a list of open ports:
    protocols = ip_results.all_protocols()
    if protocols:
        report.append([["Open ports:"]])
        for protocol in protocols:
            ports = ip_results[protocol]
            for port in ports:
                report.append([["  {}:{}".format(protocol, port)]])
    else: #No open ports for any protocol found?
        report.append([["No open ports found"]])
    #Show report
    Menu(report, i, o).activate()

def callback():
    if nmap is None:
        Printer(ffs("nmap Python module not found!", o.cols), i, o, 3)
        return False
    menu_contents = [
    ["Scan localhost", scan_localhost],
    ["Scan hardcoded IP", lambda: scan_ip("192.168.88.1")],
    ["Scan a network", scan_network_menu]
    #["Scan arbitrary IP", scan_ip],    
    ]
    Menu(menu_contents, i, o).activate()

def init_app(input, output):
    global i, o
    i = input; o = output
