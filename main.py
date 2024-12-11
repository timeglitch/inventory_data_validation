#This main function gets the dictionaries from the 3 sources and compares them

import cobbler_data_formatter
import puppet_data_formatter
import inventory_data_formatter

def main():
    cobbler_db = cobbler_data_formatter.cobbler_to_dict()
    puppet_db = puppet_data_formatter.puppet_to_dict()
    inventory_db = inventory_data_formatter.inventory_to_dict()

    cobbler_hosts = set(cobbler_db.keys())
    puppet_hosts = set(puppet_db.keys())
    inventory_hosts = set(inventory_db.keys())

    print(f"Total tracked hosts: {len(cobbler_hosts or puppet_hosts or inventory_hosts)}")
    print(f"Total hosts tracked in all 3 sources: {len(cobbler_hosts and puppet_hosts and inventory_hosts)}")

    print(f"Num hosts in cobbler but not puppet or inventory: {len(cobbler_hosts - puppet_hosts - inventory_hosts)}")
    print(f"Num hosts in puppet but not cobbler or inventory: {len(puppet_hosts - cobbler_hosts - inventory_hosts)}")
    print(f"Num hosts in inventory but not cobbler or puppet: {len(inventory_hosts - cobbler_hosts - puppet_hosts)}")

    print("Puppet and Cobbler IPv4 Mismatch:")
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['ip_address'] != cobbler_db[host]['ip_address']:
            print(f"{host}: puppet {puppet_db[host]['ip_address']} cobbler {cobbler_db[host]['ip_address']}")

    print("Puppet and Cobbler MAC Mismatch:")
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['mac_address'] != cobbler_db[host]['mac_address']:
            print(f"{host}: puppet {puppet_db[host]['mac_address']} cobbler {cobbler_db[host]['mac_address']}")

    print("Puppet and Cobbler OS Mismatch:")
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['os'] != cobbler_db[host]['os']:
            print(f"{host}: puppet {puppet_db[host]['os']} cobbler {cobbler_db[host]['os']}")

    #print(f"Hosts existing only in Cobbler:{sorted(cobbler_hosts - puppet_hosts - inventory_hosts)}") #example

    
    

main()