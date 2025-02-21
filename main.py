#This main function gets the dictionaries from the 3 sources and compares them
import cobbler_data_formatter
import puppet_data_formatter
from puppet_data_formatter import PUPPET_TO_INVENTORY_CHASSIS
import inventory_data_formatter
import sys

try:
    import tabulate
except ImportError:
    print("Please install tabulate with 'pip install tabulate'")
    exit(1)

output_to_file = False

def main():
    cobbler_db = cobbler_data_formatter.cobbler_to_dict()
    puppet_db = puppet_data_formatter.puppet_to_dict()
    inventory_db = inventory_data_formatter.inventory_to_dict()

    cobbler_hosts = set(cobbler_db.keys())
    puppet_hosts = set(puppet_db.keys())
    inventory_hosts = set(inventory_db.keys())

    print(f"Total tracked hosts: {len(cobbler_hosts or puppet_hosts or inventory_hosts)}")
    print(f"Total hosts tracked in all 3 sources: {len(cobbler_hosts and puppet_hosts and inventory_hosts)}")

    print(f"Num hosts in cobbler but not puppet or inventory: {len(cobbler_hosts - (puppet_hosts or inventory_hosts))}")
    print(f"Num hosts in puppet but not cobbler or inventory: {len(puppet_hosts - (cobbler_hosts or inventory_hosts))}")
    print(f"Num hosts in inventory but not cobbler or puppet: {len(inventory_hosts - (cobbler_hosts or puppet_hosts))}")

    print("Puppet and Cobbler IPv4 Mismatch:")
    puppet_cobbler_ipv4_mismatch = []
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['ipv4_address'].lower() != cobbler_db[host]['ipv4_address'].lower():
            puppet_cobbler_ipv4_mismatch.append([host, puppet_db[host]['ipv4_address'].lower(), cobbler_db[host]['ipv4_address'].lower()])
            #print(f"{host}: puppet {puppet_db[host]['ipv4_address']} cobbler {cobbler_db[host]['ipv4_address']}")
    if output_to_file:
        with open("puppet_cobbler_ipv4_mismatch.txt", "w") as f:
            f.write(tabulate.tabulate(puppet_cobbler_ipv4_mismatch, headers=["Host", "Puppet IPv4", "Cobbler IPv4"]))
    else:
        print(tabulate.tabulate(puppet_cobbler_ipv4_mismatch, headers=["Host", "Puppet IPv4", "Cobbler IPv4"]))

    print("Puppet and Cobbler MAC Mismatch:")
    puppet_cobbler_mac_mismatch = []
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['mac_address'].lower() != cobbler_db[host]['mac_address'].lower():
            puppet_cobbler_mac_mismatch.append([host, puppet_db[host]['mac_address'].lower(), cobbler_db[host]['mac_address'].lower()])
            #print(f"{host}: puppet {puppet_db[host]['mac_address']} cobbler {cobbler_db[host]['mac_address']}")
    if output_to_file:
        with open("puppet_cobbler_mac_mismatch.txt", "w") as f:
            f.write(tabulate.tabulate(puppet_cobbler_mac_mismatch, headers=["Host", "Puppet MAC", "Cobbler MAC"]))
    else:
        print(tabulate.tabulate(puppet_cobbler_mac_mismatch, headers=["Host", "Puppet MAC", "Cobbler MAC"]))

    print("Puppet and Cobbler OS Mismatch:")
    puppet_cobbler_os_mismatch = []
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['os_version'] != cobbler_db[host]['os_version']:
            puppet_cobbler_os_mismatch.append([host, puppet_db[host]['os_version'], cobbler_db[host]['os_version']])
            #print(f"{host}\t{puppet_db[host]['os_version']}\t{cobbler_db[host]['os_version']}")
    if output_to_file:
        with open("puppet_cobbler_os_mismatch.txt", "w") as f:
            f.write(tabulate.tabulate(puppet_cobbler_os_mismatch, headers=["Host", "Puppet Version", "Cobbler Version"]))
    else:
        print(tabulate.tabulate(puppet_cobbler_os_mismatch, headers=["Host", "Puppet Version", "Cobbler Version"]))

    #print(f"Hosts existing only in Cobbler:{sorted(cobbler_hosts - puppet_hosts - inventory_hosts)}") #example
    #print(f"Hosts existing only in Puppet:{sorted(puppet_hosts - cobbler_hosts - inventory_hosts)}")

    print("Configuration Mismatch summary:")
    print(f"IPv4 Mismatch: {len(puppet_cobbler_ipv4_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")
    print(f"MAC Mismatch: {len(puppet_cobbler_mac_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")
    print(f"OS Mismatch: {len(puppet_cobbler_os_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")    

    print("Location Mismatch:")
    puppet_inventory_location_mismatch = []
    for host in puppet_hosts & inventory_hosts:
        if puppet_db[host]["location"] != inventory_db[host]["location"]:
            puppet_inventory_location_mismatch.append([host, puppet_db[host]["location"], inventory_db[host]["location"]])
            #print(f"{host}: puppet {puppet_db[host]['location']} inventory {inventory_db[host]['location']}")
    
    if output_to_file:
        with open("puppet_inventory_location_mismatch.txt", "w") as f:
            f.write(tabulate.tabulate(puppet_inventory_location_mismatch, headers=["Host", "Puppet Location", "Inventory Location"]))
    else:
        print(tabulate.tabulate(puppet_inventory_location_mismatch, headers=["Host", "Puppet Location", "Inventory Location"]))


    print("Puppet and Inventory Model/Chassis Mismatch:")
    print("Note: if the puppet chassis name is just the hostname, it is not found to have a chassis")
    puppet_inventory_chassis_mismatch = []
    for host in puppet_hosts & inventory_hosts:
        if puppet_db[host]["chassis"] not in PUPPET_TO_INVENTORY_CHASSIS or inventory_db[host]["chassis"] not in PUPPET_TO_INVENTORY_CHASSIS[puppet_db[host]["chassis"]]: #check that the puppet chassis is in the dictionary and that the inventory chassis is in the list of possible chassis for that puppet chassis
            puppet_inventory_chassis_mismatch.append([host, puppet_db[host]["chassis"], inventory_db[host]["chassis"]])
            #print(f"{host}: puppet {puppet_db[host]['chassis']} inventory {inventory_db[host]['chassis']}")
    if output_to_file:
        with open("puppet_inventory_chassis_mismatch.txt", "w") as f:
            f.write(tabulate.tabulate(puppet_inventory_chassis_mismatch, headers=["Host", "Puppet Chassis", "Inventory Chassis"]))
    else:
        print(tabulate.tabulate(puppet_inventory_chassis_mismatch, headers=["Host", "Puppet Chassis", "Inventory Chassis"]))
    
    print("Asset Mismatch Summary:")
    print(f"Location Mismatches: {len(puppet_inventory_location_mismatch)}")
    print(f"Chassis Mismatches: {len(puppet_inventory_chassis_mismatch)}")

    #print all puppet chassis values
    """puppet_chassis = set()
    for host in puppet_hosts:
        puppet_chassis.add(puppet_db[host]["chassis"])
    puppet_chassis = sorted(puppet_chassis)
    print("Puppet Chassis Values:" + str(puppet_chassis))"""

    #print("===================Cobbler only hosts============================")
    #print(cobbler_hosts - (puppet_hosts or inventory_hosts))

# Handle command line arguments

# show help if -h or --help is passed
if "-h" in sys.argv or "--help" in sys.argv:
    print("Usage: python3 main.py")
    print("This script compares the data from the 3 sources and prints out the differences")
    print("Options:")
    print("-h, --help: Show this help message")
    print("-r, --refresh, --cobbler-refresh: Refresh the data from cobbler.chtc.wisc.edu")
    print("-F, --file: Output the results to files")
    exit(0)

if "-r" in sys.argv or "--refresh" in sys.argv or "--cobbler-refresh" in sys.argv:
    print("Refreshing data from cobbler.chtc.wisc.edu")
    cobbler_data_formatter.get_cobbler_objects()

if "-F" in sys.argv or "--file" in sys.argv:
    print("Outputting to files")
    output_to_file = True

main()