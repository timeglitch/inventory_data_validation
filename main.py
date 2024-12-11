#This main function gets the dictionaries from the 3 sources and compares them

import cobbler_data_formatter
import puppet_data_formatter
import inventory_data_formatter

def main():
    cobbler_db = cobbler_data_formatter.cobbler_to_dict()
    puppet_db = puppet_data_formatter.puppet_to_dict()
    inventory_db = inventory_data_formatter.inventory_to_dict()

    allnames = set(cobbler_db.keys()).union(set(puppet_db.keys())) #TODO: puppet keys are yamls, cobbler keys are jsons

    print("All names: ")
    print(allnames)

    print("Nodes in Cobbler but not in Puppet: ")
    print(set(cobbler_db.keys()) - set(puppet_db.keys()))

main()