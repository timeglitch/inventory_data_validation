import sys
import os
import yaml
import pprint
asset_data_path = "../asset_data"

#Couldn't figure out how to import yaml_io from the asset repository so I'm just manually reading the yamls

VALID_BUILDINGS = set(["Computer Sciences", "WID", "OneNeck", "Syracuse", "UNL", "FIU", "MISSING"])
VALID_ROOMS = {
    "Computer Sciences": set(["CS2360", "CSB240", "CS3370a"]),
    "WID": set(["WID"]),
    "OneNeck": set(["OneNeck"]),
    "Syracuse": set(["Syracuse"]),
    "UNL": set(["UNL"]),
    "FIU": set(["FIU"]),
    "MISSING": set(["MISSING"]),

}



#replaces invalid characters in the yaml files with valid ones
def preprocess_yaml_content(content: str) -> str:
    # Replace tabs with 4 spaces
    content = content.replace('\t', '    ')
    # Handle improperly escaped single quotes in double-quoted scalars
    content = content.replace("\\'", "'")
    return content


def inventory_to_dict(inventory_repository_path:str = "../asset_data") -> dict:
    db = {}

    current_assets_dir = os.path.join(asset_data_path, "current_assets")
    if not os.path.exists(current_assets_dir):
        print(f'No current_assets directory found in asset_data')
        sys.exit(1)
    #put all the nodes in the db
    nodes = os.listdir(current_assets_dir)

    #get the node's data
    for filename in nodes:
        
        #only parse config files
        if filename.endswith(".yaml"):
            filepath = os.path.join(current_assets_dir, filename)

            #open, process, and parse nodefiles
            with open(filepath, 'r') as stream:
                content = stream.read()
                content = preprocess_yaml_content(content)
                try:
                    data = yaml.safe_load(content)
                    hostname = os.path.basename(os.path.realpath(filepath)).removesuffix('.yaml')
                    db[hostname] = {}
                    db[hostname]["hostname"] = hostname #To comply with common data format
                    db[hostname]["chassis"] = data['hardware']['model']
                    db[hostname]["location"] = data['location']['building'] + ", " + data['location']['room']
                    db[hostname]["building"] = data['location']['building']
                    db[hostname]["room"] = data['location']['room']

                    #db[hostname] = data #Debug line to show raw data
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {filepath}: {e}")


    return db

def validate_location_data(db: dict) -> list[(str, str)]: #list of tuples of hostname and error message
    for hostname, data in db.items():
        building = data['building']
        if building not in VALID_BUILDINGS:
            list.append((hostname, f"Invalid building for {hostname}: {building}"))
            print(f"Invalid building for {hostname}: {building}")
        room = data['room']
        if room not in VALID_ROOMS[building]:
            list.append((hostname, f"Invalid room for {hostname}: {building} {room}"))
            print(f"Invalid room for {hostname}: {building} {room}")

#call the functions if this script is run directly
if __name__ == "__main__":
    if len(sys.argv) != 1:
        print('Usage: python3 inventory_data.py')
        print('This script loads the json files in the inventory_data repository into a dictionary')
        sys.exit(1)
    db = inventory_to_dict()

    locationerrors = validate_location_data(db)

    #pprint.pprint(db) #print the first 5 keys in the dictionary
    
