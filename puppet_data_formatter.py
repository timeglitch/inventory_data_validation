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
#convert the file names to the actual property name
YAML_TO_PROPERTIES = {
    "centos_7.yaml": "centos_7",
    "centos_8_stream.yaml": "centos_8",
    "centos_9_stream.yaml": "centos_9",
    "centos.yaml" : "centos - This is the base yaml, this shouldn\'t happen",
}

def preprocess_yaml_content(content):
    # Replace tabs with 4 spaces
    content = content.replace('\t', '    ')
    
    # Handle improperly escaped single quotes in double-quoted scalars
    content = content.replace("\\'", "'")
    
    return content

def find_nodefile_info(data): #TODO: this only works for centos 8/9
    hostname = None
    network_hostname = None
    bmc_address = None
    interfaces = []

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
                interface_info = {
                    'interface': file_key.split('/')[-1],  # Get interface name
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
                interfaces.append(interface_info)
    return hostname, network_hostname, bmc_address, interfaces

#this gets the chassis for the node and if it is a vm 
def get_node_chassis_and_vm(node_chassis_path:str) -> (str, bool):
    templatename = os.path.basename(os.path.realpath(node_chassis_path))
    #not using YAML_TO_PROPERTIES b/c the chassis yaml names should hopefully match (this may change)
    return (os.path.splitext(templatename)[0], templatename == 'kvm_guest.yaml')

#given the path to a node in os_tier_1, return the centos version of the node
def get_node_os(node_os_path:str) -> str:
    templatename = os.path.basename(os.path.realpath(node_os_path)) #extract the file name

    if templatename not in YAML_TO_PROPERTIES:
        print(f'Unknown OS template name {templatename} for node {node_os_path}') #don't know why this ever gets printed out
        return None
    return YAML_TO_PROPERTIES[templatename]

def load_yaml_files(puppet_data_path):
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
                    data = yaml.safe_load(content)
                    hostname, network_hostname, bmc_address, interfaces = find_nodefile_info(data)
                    nodes_data[filename] = {  #TODO: entries should be created even if yaml.safe_load of find_nodefile_info fails
                        'hostname': hostname,
                        'network_hostname': network_hostname,
                        'bmc_address': bmc_address,
                        'interfaces': interfaces
                    }

                    nodes_data[filename]['chassis'], nodes_data[filename]['isVM'] = get_node_chassis_and_vm(os.path.join(puppet_data_path, 'chassis', filename)) #this should be in the outside loop, but sometimes the entry for the host is not created

                    nodes_data[filename]['os_version'] = get_node_os(os.path.join(puppet_data_path, 'os_tier_1', filename))
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
        if info['bmc_address']:
            if info['bmc_address'] in bmc_addresses:
                failed_checks.append(f"Duplicate BMC address detected: {info['bmc_address']} in node {node}")
            else:
                bmc_addresses.add(info['bmc_address'])
        
        for interface in info['interfaces']:
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

def puppet_data_to_dict(puppet_data_path:str = "../puppet_data") -> dict:
    puppet_data_path = os.path.join(puppet_data_path, 'node')
    return load_yaml_files(puppet_data_path)



puppet_data_path = '../puppet_data'

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
