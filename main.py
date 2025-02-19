#This main function gets the dictionaries from the 3 sources and compares them

import cobbler_data_formatter
import puppet_data_formatter
import inventory_data_formatter

try:
    import tabulate
except ImportError:
    print("Please install tabulate with 'pip install tabulate'")
    exit(1)

puppet_to_inventory_chassis = { #should I move this to the puppet_data_formatter.py?
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
    
    puppet_cobbler_ipv4_mismatch = []
    print("Puppet and Cobbler IPv4 Mismatch:")
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['ipv4_address'].lower() != cobbler_db[host]['ipv4_address'].lower():
            puppet_cobbler_ipv4_mismatch.append([host, puppet_db[host]['ipv4_address'].lower(), cobbler_db[host]['ipv4_address'].lower()])
            #print(f"{host}: puppet {puppet_db[host]['ipv4_address']} cobbler {cobbler_db[host]['ipv4_address']}")
    print(tabulate.tabulate(puppet_cobbler_ipv4_mismatch, headers=["Host", "Puppet IPv4", "Cobbler IPv4"]))

    puppet_cobbler_mac_mismatch = []
    print("Puppet and Cobbler MAC Mismatch:")
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['mac_address'].lower() != cobbler_db[host]['mac_address'].lower():
            puppet_cobbler_mac_mismatch.append([host, puppet_db[host]['mac_address'].lower(), cobbler_db[host]['mac_address'].lower()])
            #print(f"{host}: puppet {puppet_db[host]['mac_address']} cobbler {cobbler_db[host]['mac_address']}")
    print(tabulate.tabulate(puppet_cobbler_mac_mismatch, headers=["Host", "Puppet MAC", "Cobbler MAC"]))

    print("Puppet and Cobbler OS Mismatch:")
    puppet_cobbler_os_mismatch = []
    for host in puppet_hosts & cobbler_hosts:
        if puppet_db[host]['os_version'] != cobbler_db[host]['os_version']:
            puppet_cobbler_os_mismatch.append([host, puppet_db[host]['os_version'], cobbler_db[host]['os_version']])
            #print(f"{host}\t{puppet_db[host]['os_version']}\t{cobbler_db[host]['os_version']}")
    print(tabulate.tabulate(puppet_cobbler_os_mismatch, headers=["Host", "Puppet Version", "Cobbler Version"]))

    #print(f"Hosts existing only in Cobbler:{sorted(cobbler_hosts - puppet_hosts - inventory_hosts)}") #example
    #print(f"Hosts existing only in Puppet:{sorted(puppet_hosts - cobbler_hosts - inventory_hosts)}")

    print("Software Mismatch summary:")
    print(f"IPv4 Mismatch: {len(puppet_cobbler_ipv4_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")
    print(f"MAC Mismatch: {len(puppet_cobbler_mac_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")
    print(f"OS Mismatch: {len(puppet_cobbler_os_mismatch)} / {len(puppet_hosts & cobbler_hosts)}")    

    print("Location Mismatch:")
    puppet_inventory_location_mismatch = []
    for host in puppet_hosts & inventory_hosts:
        if puppet_db[host]["location"] != inventory_db[host]["location"]:
            puppet_inventory_location_mismatch.append([host, puppet_db[host]["location"], inventory_db[host]["location"]])
            #print(f"{host}: puppet {puppet_db[host]['location']} inventory {inventory_db[host]['location']}")
    print(tabulate.tabulate(puppet_inventory_location_mismatch, headers=["Host", "Puppet Location", "Inventory Location"]))
    print("Location Mismatch Summary:")
    print(f"Number of Mismatches: {len(puppet_inventory_location_mismatch)}")
    

    print("Puppet and Inventory Model/Chassis Mismatch:")
    print("Note: if the puppet chassis name is just the hostname, it is not found to have a chassis")
    puppet_inventory_chassis_mismatch = []
    for host in puppet_hosts & inventory_hosts:
        if puppet_db[host]["chassis"] not in puppet_to_inventory_chassis or inventory_db[host]["chassis"] not in puppet_to_inventory_chassis[puppet_db[host]["chassis"]]: #check that the puppet chassis is in the dictionary and that the inventory chassis is in the list of possible chassis for that puppet chassis
            puppet_inventory_chassis_mismatch.append([host, puppet_db[host]["chassis"], inventory_db[host]["chassis"]])
            #print(f"{host}: puppet {puppet_db[host]['chassis']} inventory {inventory_db[host]['chassis']}")
    print(tabulate.tabulate(puppet_inventory_chassis_mismatch, headers=["Host", "Puppet Chassis", "Inventory Chassis"]))
    print("Chassis Mismatch Summary:")
    print(f"Number of Mismatches: {len(puppet_inventory_chassis_mismatch)}")

    #print all puppet chassis values
    """puppet_chassis = set()
    for host in puppet_hosts:
        puppet_chassis.add(puppet_db[host]["chassis"])
    puppet_chassis = sorted(puppet_chassis)
    print("Puppet Chassis Values:" + str(puppet_chassis))"""

    #print("===================Cobbler only hosts============================")
    #print(cobbler_hosts - (puppet_hosts or inventory_hosts))
main()