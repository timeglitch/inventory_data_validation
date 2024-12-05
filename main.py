#This main function gets the dictionaries from the 3 sources and compares them

import inventory_data_validation.cobbler_data_formatter as cobbler_data_formatter


def main():
    cobbler_db = cobbler_data_formatter.cobbler_to_dict()