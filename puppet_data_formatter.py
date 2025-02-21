# https://opensciencegrid.atlassian.net/browse/INF-2154
# hostname from file
# BMC configuration or lackthereof
# including IP address
# interfaces
# ipv4/6 addrs and MAC addresses per interface, as well as type of interface
# hostname set in networking files
#   Then we can use that data structure for fun internal parity checks:
# No duplicate IP4 addresses between BMCs
# No duplicate IPv4/6 addresses between primary NICs
# Primary NICs should have mac addresses, unless they are infiniband
# Lack of IPV6 configuration
# If assigned IPv6 address is not proper EUI64 for the mac address set
# and so on. Virtual devices (which can be determined via symlink) should not have BMCs.
import os
import yaml
import sys
import pprint
from typing import Tuple

#convert the file names to the actual property name
YAML_TO_PROPERTIES = {
    "centos_7.yaml": "centos_7",
    "centos_8_stream.yaml": "centos_8",
    "centos_9_stream.yaml": "centos_9",
    "centos.yaml" : "centos - This is the base yaml, this shouldn\'t happen",
    #location property names are in the format: "BUILDING, ROOM".  If there is no room, it is "BUILDING, BUILDING"
    "cs_2360.yaml" : "Computer Sciences, CS2360",
    "cs_3370a.yaml" : "Computer Sciences, CS3370a",
    "cs_b240.yaml" : "Computer Sciences, CSB240",
    "oneneck.yaml" : "OneNeck, OneNeck",
    "path_fiu.yaml" : "FIU, FIU",
    "path_syra.yaml" : "Syracuse, Syracuse", #syra seems to be in syracuse
    "path_syrb.yaml" : "Computer Sciences, CS2360", #syrb seems to be in cs2360
    "path_unl.yaml" : "UNL, UNL",
    "path_wisc.yaml" : "Computer Sciences, CS2360", #TODO: it appears they live in cs2360
    "wid.yaml" : "WID, WID",
}


PUPPET_TO_INVENTORY_CHASSIS = { #This is used by main.py, but held here for now
    'ars-210m-nr' : ["ARS-210M-NR"], 
    'as-1015cs-tnr' : ["AS -1015CS-TNR", "AS-1015CS-TNR"], #not sure about the spelling but who am i to complain 
    'as-1115hs-tnr' : ["AS-1115HS-TNR", "Supermicro AS-1115HS-TNR", "SuperMicro HS119-R12H13"], #this one template seems to have two models as well
    'as-2124gq-nart' : ["AS-2124GQ-NART", "SuperMicro AS -2124GQ-NART", "Supermicro AS-2124GQ-NART"], 
    'as-4124go-nart' : ["AS-4124GO-NART", "Supermicro AS-4124GO-NART", "Supermicro AS -4124GO-NART"], 
    'as-4124gs-tnr' : ["AS-4124GS-TNR", "Supermicro AS-4124GS-TNR", "Supermicro AS -4124GS-TNR"],
    'b7105f48tv8hr-2t-g' : ["Tyan B7105F48TV8HR-2T-G"],
    'esc8000-e11' : ["ADS ESC8000-E11", "ASUSTeK ESC8000A-E11"],
    'esc8000a-e11' : ["ADS ESC8000A-E11", "ASUSTeK ESC8000A-E11"],
    'g291-280-00' : ["Gigabyte G291-280-00"],

    'poweredge_c6220_1' : ["PowerEdge C6220", "Dell PowerEdge C6220", "Dell EMC PowerEdge C6220", "Dell EMC C6220"], 
    "poweredge_c6420" : ["PowerEdge C6420", "Dell PowerEdge C6420", "Dell EMC PowerEdge C6420", "Dell EMC C6420", 
                         "PowerEdge C6400", "Dell PowerEdge C6400", "Dell EMC PowerEdge C6400", "Dell EMC C6400"], #looks like these two chassis are similar enough to have the same manual and the same entry
    'poweredge_c6525' : ["PowerEdge C6525", "Dell PowerEdge C6525", "Dell EMC PowerEdge C6525", "Dell EMC C6525"], 
    'poweredge_r310' : ["PowerEdge R310", "Dell PowerEdge R310", "Dell EMC PowerEdge R310", "Dell EMC R310"],
    'poweredge_r410' : ["PowerEdge R410", "Dell PowerEdge R410", "Dell EMC PowerEdge R410", "Dell EMC R410"],
    'poweredge_r415' : ["PowerEdge R415", "Dell PowerEdge R415", "Dell EMC PowerEdge R415", "Dell EMC R415"],
    'poweredge_r510' : ["PowerEdge R510", "Dell PowerEdge R510", "Dell EMC PowerEdge R510", "Dell EMC R510"],
    'poweredge_r515' : ["PowerEdge R515", "Dell PowerEdge R515", "Dell EMC PowerEdge R515", "Dell EMC R515"],
    'poweredge_r520' : ["PowerEdge R520", "Dell PowerEdge R520", "Dell EMC PowerEdge R520", "Dell EMC R520"],
    'poweredge_r640' : ["PowerEdge R640", "Dell PowerEdge R640", "Dell EMC PowerEdge R640", "Dell EMC R640"],
    'poweredge_r6525' : ["PowerEdge R6525", "Dell PowerEdge R6525", "Dell EMC PowerEdge R6525", "Dell EMC R6525"],
    'poweredge_r720xd' : ["PowerEdge R720xd", "Dell PowerEdge R720xd", "Dell EMC PowerEdge R720xd", "Dell EMC R720xd"],
    'poweredge_r730' : ["PowerEdge R730", "Dell PowerEdge R730", "Dell EMC PowerEdge R730", "Dell EMC R730"],
    'poweredge_r730xd' : ["PowerEdge R730xd", "Dell PowerEdge R730xd", "Dell EMC PowerEdge R730xd", "Dell EMC R730xd"],
    'poweredge_r740' : ["PowerEdge R740", "Dell PowerEdge R740", "Dell EMC PowerEdge R740", "Dell EMC R740"],
    'poweredge_r740xd' : ["PowerEdge R740xd", "Dell PowerEdge R740xd", "Dell EMC PowerEdge R740xd", "Dell EMC R740xd"],
    'poweredge_r750' : ["PowerEdge R750", "Dell PowerEdge R750", "Dell EMC PowerEdge R750", "Dell EMC R750"],
    'poweredge_r750xa' : ["PowerEdge R750xa", "Dell PowerEdge R750xa", "Dell EMC PowerEdge R750xa", "Dell EMC R750xa"],
    'poweredge_r815' : ["PowerEdge R815", "Dell PowerEdge R815", "Dell EMC PowerEdge R815", "Dell EMC R815"],
    'poweredge_r920' : ["PowerEdge R920", "Dell PowerEdge R920", "Dell EMC PowerEdge R920", "Dell EMC R920"],
    'poweredge_r930' : ["PowerEdge R930", "Dell PowerEdge R930", "Dell EMC PowerEdge R930", "Dell EMC R930"],
    'poweredge_r940xa' : ["PowerEdge R940xa", "Dell PowerEdge R940xa", "Dell EMC PowerEdge R940xa", "Dell EMC R940xa"],
    'poweredge_xe8545' : ["PowerEdge XE8545", "Dell PowerEdge XE8545", "Dell EMC PowerEdge XE8545", "Dell EMC XE8545"],

    'r283-z96-aae1' : ["R283-Z96-AAE1", "R283-Z96-AAE1-000"],
    'ssg-6029p-e1cr24h' : ["King Star SSG-6029P-E1CR24H"],
    'sys-1029gq-trt' : ["SuperMicro SYS-1029GQ-TRT", "SYS-1029GQ-TRT"],
    'sys-221h-tn24r' : ["SuperMicro SYS-221H-TN24R", "SYS-221H-TN24R"],
    'sys-420gp-tnr' : ["SuperMicro SYS-420GP-TNR", "SYS-420GP-TNR", "sys-420gp-tnr"],
    'sys-7049gp-trt' : ["SuperMicro SYS-7049GP-TRT", "SYS-7049GP-TRT", "sys-7049gp-trt"],
    'sys-821ge-tnhr' : ["SuperMicro SYS-821GE-TNHR", "SYS-821GE-TNHR", "sys-821ge-tnhr"],
    'sys-f617r2-rt' : ["SuperMicro SYS-F617R2-RT", "SYS-F617R2-RT", "SYS-F617R2-RT+", "sys-f617r2-rt"],
    'ucsc_c220_m3s' : ["Cisco UCS C220 M3"],
    'x9dr3-f' : ["SuperMicro X9DR3-F", "X9DR3-F"],

}


def preprocess_yaml_content(content: str) -> str:
    # Replace tabs with 4 spaces
    content = content.replace('\t', '    ')
    # Handle improperly escaped single quotes in double-quoted scalars
    content = content.replace("\\'", "'")
    return content

from typing import List

#this function takes the dict of a nodefile and extracts the hostname, network hostname, bmc address, and interfaces
#interfaces are returned in a dict with key = interface name (e.g. eth0) and value = dict of HWADDR, IPADDR, IPV6ADDR
def find_nodefile_info(data: dict, os_version: str) -> Tuple[str, str, str, dict]: #this function is super ugly, maybe refactor
    hostname = None             #hostname and network hostname are currently unused for centos7, just a bonus validation
    network_hostname = None
    bmc_address = None
    interfaces = {}

    if os_version == 'centos_7': #
        # print("\nCentOS 7 data['network']:")
        # pprint.pprint(data['network'])
        
        if 'network' not in data:
            #print("=============== No network data found in CentOS 7 node file.") #this isn't suprising if we have: {materialize: false}, so we don't print this message
            return None, None, None, None
        if 'if_bridge' not in data['network']:
            print("=============== No if_bridge data found in CentOS 7 node file.")
            return None, None, None, None
        if 'eth0' not in data['network']['if_bridge']:
            print("=============== No eth0 data found in CentOS 7 node file, interfaces are: " + str(data['network'].keys()))
            return None, None, None, None
        if 'bridge_static' not in data['network']:
            print("=============== No bridge_static data found in CentOS 7 node file.")
            return None, None, None, None
        if 'br0' not in data['network']['bridge_static']:
            print("=============== No br0 data found in CentOS 7 node file.")
            return None, None, None, None
        
        if 'bmc' in data and 'lan' in data['bmc'] and 'ip_address' in data['bmc']['lan']:
            bmc_address = data['bmc']['lan']['ip_address']

        interface_info = {
            'interface': 'eth0', #eth0 is the only interface we care about for centos7 (TODO: check to make sure this is true)
            'HWADDR': None,
            'IPADDR': None,
            'IPV6ADDR': None
        }

        if data['network']['if_bridge']['eth0']: #if eth0 is a dictionary with a value
            if data['network']['if_bridge']['eth0'] and 'macaddress' in data['network']['if_bridge']['eth0']:
                interface_info['HWADDR'] = data['network']['if_bridge']['eth0'].get('macaddress') #dict.get(key) returns None if key doesn't 
                
            if data['network']['bridge_static']['br0'] and 'ipaddress' in data['network']['bridge_static']['br0']:
                interface_info['IPADDR'] = data['network']['bridge_static']['br0'].get('ipaddress')

            if data['network']['bridge_static']['br0'] and 'ipv6address' in data['network']['bridge_static']['br0']:
                interface_info['IPV6ADDR'] = data['network']['bridge_static']['br0'].get('ipv6address')
        else: #if eth0 is false or null, meaning that data probably exists in a bond_bridge
            pass
            #TODO: get the data from the bond_bridge




        interfaces['eth0'] = interface_info
        
        return hostname, network_hostname, bmc_address, interfaces

    elif os_version == 'centos_8' or os_version == 'centos_9':
        # print("CentOS 8/9 data")
        # if 'file' in data:
        #     pprint.pprint({k:v for (k,v) in data["file"].items() if '/etc/sysconfig/network-scripts' in k})

        if 'bmc' in data and 'lan' in data['bmc'] and 'ip_address' in data['bmc']['lan']:
            bmc_address = data['bmc']['lan']['ip_address']
        
        if 'file' in data:
            if '/etc/hostname' in data['file'] and 'content' in data['file']['/etc/hostname']:
                hostname_content = data['file']['/etc/hostname']['content']
                for key, value in hostname_content.items():
                    if isinstance(value, dict):
                        for host, flag in value.items():
                            if flag:  # Check if it's set to True
                                hostname = host
            if '/etc/sysconfig/network' in data['file'] and 'content' in data['file']['/etc/sysconfig/network']:
                network_content = data['file']['/etc/sysconfig/network']['content']
                for key, value in network_content.items():
                    if isinstance(value, dict):
                        for network_config, flag in value.items():
                            if flag and network_config.startswith("HOSTNAME="):
                                network_hostname = network_config.split('=')[1]

            # Loop through all the interfaces in /etc/sysconfig/network-scripts/
            for file_key, file_value in data['file'].items():
                if file_key.startswith('/etc/sysconfig/network-scripts/ifcfg-') and 'content' in file_value:
                    interfacename = file_key.removeprefix('/etc/sysconfig/network-scripts/ifcfg-')  # Get interface name, removeprefix() behavior is kinda weird but this should work

                    interface_info = {
                        'interface': file_key.split('/')[-1], #keeping this for parity checks
                        'HWADDR': None,
                        'IPADDR': None,
                        'IPV6ADDR': None
                    }
                    eth_content = file_value['content']
                    for key, value in eth_content.items():
                        if isinstance(value, dict):
                            for network_config, flag in value.items():
                                if flag and network_config.startswith("HWADDR="):
                                    interface_info['HWADDR'] = network_config.split('=')[1]
                                if flag and network_config.startswith("IPADDR="):
                                    interface_info['IPADDR'] = network_config.split('=')[1]
                                if flag and network_config.startswith("IPV6ADDR="):
                                    interface_info['IPV6ADDR'] = network_config.split('=')[1]
                    interfaces[interfacename] = interface_info
        return hostname, network_hostname, bmc_address, interfaces
    else:
        print(f"Unknown OS version {os_version}")
        return None, None, None, None

#this gets the chassis for the node and if it is a vm 
def get_node_chassis_and_vm(node_chassis_path:str) -> Tuple[str, bool]:
    templatename = os.path.basename(os.path.realpath(node_chassis_path))
    if ".chtc.wisc.edu" in templatename: #if the file is not a symlink, then return false
        return ("unknown", False)
    #not using YAML_TO_PROPERTIES b/c the chassis yaml names should hopefully match (this may change)
    return ("vm" if templatename == 'kvm_guest.yaml' else os.path.splitext(templatename)[0], templatename == 'kvm_guest.yaml')

#given the path to a node in os_tier_1, return the centos version of the node
def get_node_os(node_os_path:str) -> str:
    templatename = os.path.basename(os.path.realpath(node_os_path)) #extract the file name

    if templatename not in YAML_TO_PROPERTIES:
        print(f'Unknown OS template name {templatename} for node {node_os_path}') #don't know why this ever gets printed out
        return None
    return YAML_TO_PROPERTIES[templatename]

def get_node_site(node_site_path:str) -> str:
    templatename = os.path.basename(os.path.realpath(node_site_path)) #extract the file name

    if templatename not in YAML_TO_PROPERTIES:
        print(f'Unknown Site name {templatename} for node {node_site_path}') #don't know why this ever gets printed out
        return None
    return YAML_TO_PROPERTIES[templatename]

def load_yaml_files(puppet_data_path: str) -> dict:
    nodes_data = {}
    for filename in os.listdir(os.path.join(puppet_data_path, 'node')):
        
        #only parse config files
        if filename.endswith(".yaml"):
            filepath = os.path.join(puppet_data_path, 'node', filename)

            #open, process, and parse nodefiles
            with open(filepath, 'r') as stream:
                content = stream.read()
                content = preprocess_yaml_content(content)
                try:
                    hostname = os.path.basename(os.path.realpath(filepath)).removesuffix('.yaml') #we need the fqdn for hostname
                    
                    data = yaml.safe_load(content)
                    #print(f"Processing {hostname}")

                    nodes_data[hostname] = {}

                    nodes_data[hostname]['chassis'], nodes_data[hostname]['isVM'] = get_node_chassis_and_vm(os.path.join(puppet_data_path, 'chassis_tier_0', filename)) #this should be in the outside loop, but sometimes the entry for the host is not created
                    nodes_data[hostname]['os_version'] = get_node_os(os.path.join(puppet_data_path, 'os_tier_1', filename))
                    
                    nodes_data[hostname]['location'] = get_node_site(os.path.join(puppet_data_path, 'site_tier_0', filename)) #the location key is used to compare against inventory

                    name, network_hostname, bmc_address, interfaces = find_nodefile_info(data, nodes_data[hostname]['os_version'])
                    if (name is not None and not (name == hostname.split('.')[0] or name == hostname)): # make sure name isn't none, and that name isn't just the hostname or the fqdn
                        print(f"Hostname mismatch: {name} != {hostname}")
                    
                    nodes_data[hostname]['hostname'] = hostname
                    nodes_data[hostname]['network_hostname'] = network_hostname
                    nodes_data[hostname]['bmc_address'] = bmc_address
                    nodes_data[hostname]['interfaces'] = interfaces #keep for parity checks
                    
                    # Add interfaces to the node data
                    # Only add the most relevant interface
                    nodes_data[hostname]["mac_address"] = ""
                    nodes_data[hostname]["ipv4_address"] = ""
                    # nodes_data[hostname]["netmask"] = ""
                    # nodes_data[hostname]["gateway"] = ""
                    nodes_data[hostname]["ipv6_address"] = ""
                    if interfaces is not None and len(interfaces) > 0: #only do this if we actually have an interface to look at
                        for ifkey in list(interfaces.keys()) + ["em1", "eth0", "ib0"]: #make sure we do some specific interfaces last TODO: get help on which interface provides the "real" address
                            if ifkey not in interfaces:
                                continue

                            for nodedictkey, ifdictkey in [('mac_address', 'HWADDR'), ('ipv4_address', 'IPADDR'), ('ipv6_address', 'IPV6ADDR')]:
                                if interfaces[ifkey][ifdictkey] is not None and interfaces[ifkey][ifdictkey] != "":

                                    nodes_data[hostname][nodedictkey] = interfaces[ifkey][ifdictkey]
                            # nodes_data[hostname]["mac_address"] = if interfaces[ifkey]['HWADDR'] is None else interfaces[ifkey]['HWADDR'].upper()
                            # nodes_data[hostname]["ipv4_address"] = interfaces[ifkey]['IPADDR']
                            # # nodes_data[hostname]["netmask"] = interfaces[ifkey]['netmask']
                            # # nodes_data[hostname]["gateway"] = interfaces[ifkey]['if_gateway']
                            # nodes_data[hostname]["ipv6_address"] = interfaces[ifkey]['IPV6ADDR']

                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {filepath}: {e}")
    return nodes_data


def perform_parity_checks(nodes_data):
    ipv4_addresses = set()
    ipv6_addresses = set()
    bmc_addresses = set()
    failed_checks = []
    for node, info in nodes_data.items():
        # Check for duplicate BMC addresses
        # print("====================================")
        # print(node)
        # print(info)
        
        if (info is None or len(info) == 0):
            print(f"Node {node} has no data.")
            continue

        if info['bmc_address']:
            if info['bmc_address'] in bmc_addresses:
                failed_checks.append(f"Duplicate BMC address detected: {info['bmc_address']} in node {node}")
            else:
                bmc_addresses.add(info['bmc_address'])
        if (info['interfaces'] is None or len(info['interfaces']) == 0):
            continue
        for interface in info['interfaces'].values():
            # Check for duplicate IPv4/IPv6 addresses
            if interface['IPADDR']:
                if interface['IPADDR'] in ipv4_addresses:
                    failed_checks.append(f"Duplicate IPv4 address detected: {interface['IPADDR']} in node {node}")
                else:
                    ipv4_addresses.add(interface['IPADDR'])
            
            if interface['IPV6ADDR']:
                if interface['IPV6ADDR'] in ipv6_addresses:
                    failed_checks.append(f"Duplicate IPv6 address detected: {interface['IPV6ADDR']} in node {node}")
                else:
                    ipv6_addresses.add(interface['IPV6ADDR'])
            
            # TODO: Check if primary NICs have HWADDR unless they are virtual devices
            if interface['interface'].startswith("ifcfg-eth") and not interface['HWADDR']:
                failed_checks.append(f"Primary NIC {interface['interface']} in node {node} has no HWADDR.")
            
            # Check for missing IPV6 configuration
            if not interface['IPV6ADDR']:
                failed_checks.append(f"Interface {interface['interface']} in node {node} is missing an IPV6 address.")

    return failed_checks

def puppet_to_dict(puppet_data_path:str = "../puppet_data") -> dict:
    return load_yaml_files(puppet_data_path)



if __name__ == "__main__":
    puppet_data_path = '../puppet_data' #TODO: change this back to '../puppet_data' when done testing
    #run this if called through command line
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print('Usage: python3 puppet_data.py [path_to_puppet_data]')
            print('This script loads the json files in the puppet_data repository into a dictionary')
            sys.exit(0)
        else:
            puppet_data_path = sys.argv[1]
    # Running this file with no args will run the parity checks
    nodes_data = load_yaml_files(puppet_data_path)
    parity_check_results = perform_parity_checks(nodes_data)
    if parity_check_results:
        print("Parity Check Failures:")
        for failure in parity_check_results:
            print(failure)
    else:
        print("All parity checks passed.")

    #pprint.pprint(nodes_data) #print everything
