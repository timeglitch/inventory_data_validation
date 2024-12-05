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

def preprocess_yaml_content(content):
    # Replace tabs with 4 spaces
    content = content.replace('\t', '    ')
    
    # Handle improperly escaped single quotes in double-quoted scalars
    content = content.replace("\\'", "'")
    
    return content

def find_info(data): #TODO: this only works for centos 8/9
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


def load_yaml_files(directory):
    nodes_data = {}
    for filename in os.listdir(directory):
        
        #only parse config files
        if filename.endswith(".yaml"):
            filepath = os.path.join(directory, filename)

            with open(filepath, 'r') as stream:
                content = stream.read()
                content = preprocess_yaml_content(content)
                try:
                    data = yaml.safe_load(content)
                    hostname, network_hostname, bmc_address, interfaces = find_info(data)
                    nodes_data[filename] = {
                        'hostname': hostname,
                        'network_hostname': network_hostname,
                        'bmc_address': bmc_address,
                        'interfaces': interfaces
                    }
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


directory = '../puppet_data/node/'
nodes_data = load_yaml_files(directory)
parity_check_results = perform_parity_checks(nodes_data)
if parity_check_results:
    print("Parity Check Failures:")
    for failure in parity_check_results:
        print(failure)
else:
    print("All parity checks passed.")