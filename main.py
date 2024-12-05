#This main function gets the dictionaries from the 3 sources and compares them

import cobbler_data


def main():
    cobbler_db = cobbler_data.cobbler_to_dict()