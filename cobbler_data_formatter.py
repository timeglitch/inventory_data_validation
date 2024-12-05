# This script puts the json files in cobbler_objects into a dictionary
import json
import os
import pprint
import sys


#copies the cobbler_objects directory from cobbler.chtc.wisc.edu
def get_cobbler_objects():
    os.system('scp -r cobbler.chtc.wisc.edu:/var/lib/cobbler/config/systems.d cobbler_objects')
#first check that cobbler_objects exists, if not scp from cobbler.chtc.wisc.edu
if not os.path.exists('cobbler_objects'):
    os.system('scp -r cobbler.chtc.wisc.edu:/var/lib/cobbler/config/systems.d cobbler_objects')

#TODO: maybe rsync to make sure the files are up to date?

#requires the cobbler_objects directory to exist
#returns a dictionary of the json files in cobbler_objects
#redownload_files: if True, will re-download the files from cobbler.chtc.wisc.edu
def cobbler_to_dict(redownload_files:bool=False) -> dict:

    #first check that cobbler_objects exists, if not scp from cobbler.chtc.wisc.edu
    if redownload_files or (not os.path.exists('cobbler_objects')):
        os.system('scp -r cobbler.chtc.wisc.edu:/var/lib/cobbler/config/systems.d cobbler_objects')

    #now load the json files into a dictionary
    db = {}
    files = os.listdir('cobbler_objects')

    for file in files:
        if file.endswith('.json'):
            with open(f'cobbler_objects/{file}', 'r') as f:
                data = json.load(f)
                db[file] = data
                if file.removesuffix('.json') != data['hostname']:
                    print(f'Filename "{file}" does not match hostname entry "{data["hostname"]}"') #TODO: return this data more intelligently?
                else:
                    print(f'Loaded {file} into dictionary')              
        else:
            print(f'{file} is not a json file')

    return db

#example entry looks like this:
"""
{'boot_files': {},
 'comment': '',
 'ctime': 1666377201.884356,
 'depth': 3,
 'enable_gpxe': False,
 'fetchable_files': {},
 'gateway': '',
 'hostname': 'spark-a055.chtc.wisc.edu',
 'image': '',
 'interfaces': {'ib0': {'bonding_opts': '',
                        'bridge_opts': '',
                        'cnames': [],
                        'connected_mode': False,
                        'dhcp_tag': 'chtc',
                        'dns_name': 'spark-a055.chtc.wisc.edu',
                        'if_gateway': '',
                        'interface_master': '',
                        'interface_type': 'infiniband',
                        'ip_address': '10.130.203.62',
                        'ipv6_address': '',
                        'ipv6_default_gateway': '',
                        'ipv6_mtu': '',
                        'ipv6_prefix': '',
                        'ipv6_secondaries': [],
                        'ipv6_static_routes': [],
                        'mac_address': 'e8:eb:d3:40:28:64',
                        'management': False,
                        'mtu': '',
                        'netmask': '',
                        'static': False,
                        'static_routes': [],
                        'virt_bridge': 'br0'}},
 'ipv6_autoconfiguration': False,
 'ipv6_default_device': '',
 'kernel_options': {'console': 'tty0'},
 'kernel_options_post': {},
 'kickstart': '<<inherit>>',
 'ks_meta': {},
 'ldap_enabled': False,
 'ldap_type': 'authconfig',
 'mgmt_classes': '<<inherit>>',
 'mgmt_parameters': '<<inherit>>',
 'monit_enabled': False,
 'mtime': 1724094208.886704,
 'name': 'spark-a055.chtc.wisc.edu',
 'name_servers': [],
 'name_servers_search': [],
 'netboot_enabled': False,
 'owners': ['admin'],
 'power_address': '',
 'power_id': '',
 'power_pass': '',
 'power_type': 'ipmitool',
 'power_user': '',
 'profile': 'CentOS_9_Stream_r10k_puppet8_IB',
 'proxy': '<<inherit>>',
 'redhat_management_key': '<<inherit>>',
 'redhat_management_server': '<<inherit>>',
 'repos_enabled': False,
 'server': '<<inherit>>',
 'status': 'production',
 'template_files': {},
 'template_remote_kickstarts': 1,
 'uid': 'MTY2NjM3NzIwMS44ODgyNzkxNDIuNDY4Mjc',
 'virt_auto_boot': 0,
 'virt_cpus': '<<inherit>>',
 'virt_disk_driver': '<<inherit>>',
 'virt_file_size': '<<inherit>>',
 'virt_path': '<<inherit>>',
 'virt_pxe_boot': 0,
 'virt_ram': '<<inherit>>',
 'virt_type': 'xenpv'}
"""
#call the functions if this script is run directly


if len(sys.argv) != 1:
    print('Usage: python3 cobbler_data.py')
    print('This script copies cobbler_objects from cobbler.chtc.wisc.edu and loads the json files into a dictionary')
    sys.exit(1)


db = cobbler_to_dict()
pprint.pprint(db[next(iter(db))])
