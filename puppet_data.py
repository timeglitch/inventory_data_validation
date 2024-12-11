#DEAD FILE: this file is no longer used, use puppet_data_formatter.py instead
#it's just here for reference

#This files gathers data from puppet and puts it into a dictionary


import yaml
import os
import pprint
import sys

#convert the file names to the actual property name
yaml_to_properties = {
    "centos_7.yaml": "centos_7",
    "centos_8_stream.yaml": "centos_8",
    "centos_9_stream.yaml": "centos_9",
    "centos.yaml" : "centos - This is the base yaml, this shouldn\'t happen",
}

#given the path to a node in os_tier_1, return the centos version of the node
def get_node_os(node_os_path:str) -> str:
    templatename = os.path.basename(os.path.realpath(node_os_path)) #extract the file name

    if templatename not in yaml_to_properties:
        print(f'Unknown OS template name {templatename} for node {node_os_path}') #don't know why this gets printed out
        return None
    return yaml_to_properties[templatename]

#this gets the chassis for the node and if it is a vm 
def get_node_chassis_and_vm(node_chassis_path:str) -> (str, bool):
    templatename = os.path.basename(os.path.realpath(node_chassis_path))
    #not using yaml_to_properties b/c the chassis yaml names should hopefully match (this may change)
    return (os.path.splitext(templatename)[0], templatename == 'kvm_guest.yaml')

def read_nodefile(nodefile_path:str, os_version:str = 'centos_9_stream.yaml') -> dict:
    if not os.path.exists(nodefile_path):
        print(f'Nodefile {nodefile_path} does not exist')
        return None

    with open(nodefile_path, 'r') as f:
        try:
            data = yaml.safe_load(f)
            print(f"Node {nodefile_path} \tloaded\r", flush=True, end='')
            
        except yaml.YAMLError as e:
            print(f'Error loading {nodefile_path}: {e}')
            return 
    
    ip_address = None
    mac_address = None
    ipv6_address = None
    gateway = None
    if (os_version == "centos_7"):
        try:
            ip_address = data['network']['bridge_static']['br0']['ipaddress']
            mac_address = data['network']['if_bridge']['eth0']['macaddress']
            if('ipv6_address' in data['network']['bridge_static']['br0']):
                ipv6_address = data['network']['bridge_static']['br0']['ipv6address']
            if('default_gateway' in data['network']):
                gateway = data['network']['default_gateway']
        except KeyError as e:
            print(f'Keyerror loading {nodefile_path}: {e}')
            return
        except TypeError as e:
            #raise e
            print(f'TypeError loading {nodefile_path}: {e}')
            return

    elif (os_version == "centos_8" or os_version == "centos_9"):
        pass
    else:
        print(f'Unknown OS version {os_version} for nodefile {nodefile_path}')

    output = (ip_address, mac_address, ipv6_address, gateway)
    #print(f'Nodefile {nodefile_path} has output {output}')

    return data
    

#requires the puppet_data repository to exist locally, takes in a path to the puppet_data repository
def read_puppet_data(puppet_data_path:str = "../puppet_data") -> dict:
    db = {}
    directories = os.listdir(puppet_data_path)

    if 'node' not in directories:
        print('No node directory found in puppet_data')
        sys.exit(1)
    #put all the nodes in the db
    nodes = os.listdir(os.path.join(puppet_data_path, 'node'))
    print("Some of the nodes: ", nodes[:10])

    numnodes = len(nodes)

    for count, node in enumerate(nodes):

        print(f'Loading node {node: <60} \t({count}/{numnodes})\r', flush=True, end='')
        nodename = node.sptrip('.yaml')
        db[nodename] = {} #initialize the node 
        db[nodename]["hostname"] = node #TODO: get the hostname from the nodefile


        db[nodename]["os_version"] = get_node_os(os.path.join(puppet_data_path, 'os_tier_1', node)) #getting the os first b/c nodefiles format depend on it
        db[nodename]["chassis"], db[nodename]["isVM"] = get_node_chassis_and_vm(os.path.join(puppet_data_path, 'chassis', node)) #set the chassis and vm value

        #this is temporary
        tmp = read_nodefile(os.path.join(puppet_data_path, 'node', node), db[nodename]["os_version"])
        db[nodename]["nodefile"] = tmp

        #db[nodename]["ipv4_address"], db[nodename]["netmask"], db[nodename]["gateway"],  = tmp

    centos7examples = """e474.chtc.wisc.edu.yaml
                    e2288.chtc.wisc.edu.yaml
                    e2363.chtc.wisc.edu.yaml
                    hypervisor0004.chtc.wisc.edu.yaml
                    e365.chtc.wisc.edu.yaml
                    e2440.chtc.wisc.edu.yaml
                    e323.chtc.wisc.edu.yaml
                    tiger0032.chtc.wisc.edu.yaml
                    e560.chtc.wisc.edu.yaml
                    es0003.chtc.wisc.edu.yaml
                    e2400.chtc.wisc.edu.yaml"""
    for s in centos7examples.split():
        print("===========================================")
        print(s)
        pprint.pprint(db[s]["nodefile"])
    print("===========================================")


    


#run this if called through command line

if len(sys.argv) == 1:
    read_puppet_data()
elif len(sys.argv) == 2:
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print('Usage: python3 puppet_data.py [path_to_puppet_data]')
        print('This script loads the json files in the puppet_data repository into a dictionary')
        sys.exit(0)
    else:
        read_puppet_data(sys.argv[1])