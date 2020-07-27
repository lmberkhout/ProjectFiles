import pandas as pd
from hera_mc import cm_sysutils
import json
new_nodes = {'20201001': ['N01', 'N02', 'N15']}

# #############################################
# HERE IS WHERE TO CHANGE
# options are N06, N11, N16 - N29; see heraSite.pdf
new_nodes['20201101'] = ['N20']
new_nodes['20201201'] = ['N19']
new_nodes['20210101'] = ['N18']
new_nodes['20210201'] = ['N16']
new_nodes['20210301'] = ['N11']

# #############################################

ants = {}
installed = pd.read_csv('installed_200717.csv')
nodes = cm_sysutils.which_node(list(installed['name']))
active = pd.read_csv('active_200717.csv')

this_date = '20200801'
ants[this_date] = {}
active_nodes = set()
for i in range(active.shape[0]):
    this_stn = int(active.name[i][2:])
    this_node = int(nodes[this_stn][0][1:])
    active_nodes.add(nodes[this_stn][0])
    this_row = active.loc[active.name == active.name[i]]
    ants[this_date][this_stn] = {
                                'node': this_node,
                                'easting': this_row.easting.values[0],
                                'northing': this_row.northing.values[0],
                                'latitude': this_row.latitude.values[0],
                                'longitude': this_row.longitude.values[0],
                                'elevation': this_row.elevation.values[0],
                                'X': this_row.X.values[0],
                                'Y': this_row.Y.values[0],
                                'Z': this_row.Z.values[0]
    }

dates_used = ['20200801']
for this_date in sorted(new_nodes.keys()):
    add_nodes = new_nodes[this_date]
    ants[this_date] = {}
    for ai, av in ants[dates_used[-1]].items():
        ants[this_date][ai] = av
    dates_used.append(this_date)
    for this_stn, nv in nodes.items():
        if nv[0] in add_nodes:
            stn_name = "HH{}".format(this_stn)
            this_node = int(nv[0][1:])
            this_row = installed.loc[installed.name == stn_name]
            ants[this_date][this_stn] = {
                                        'node': this_node,
                                        'easting': this_row.easting.values[0],
                                        'northing': this_row.northing.values[0],
                                        'latitude': this_row.latitude.values[0],
                                        'longitude': this_row.longitude.values[0],
                                        'elevation': this_row.elevation.values[0],
                                        'X': this_row.X.values[0],
                                        'Y': this_row.Y.values[0],
                                        'Z': this_row.Z.values[0]
            }

this_date = '20210301'
outriggers = ['HH139', 'HH159', 'HH146', 'HH76', 'HA330', 'HA334', 'HA338']
this_node = 'N12'
for stn_name in outriggers:
    this_row = installed.loc[installed.name == stn_name]
    this_stn = int(stn_name[2:])
    ants[this_date][this_stn] = {
                                'node': this_node,
                                'easting': this_row.easting.values[0],
                                'northing': this_row.northing.values[0],
                                'latitude': this_row.latitude.values[0],
                                'longitude': this_row.longitude.values[0],
                                'elevation': this_row.elevation.values[0],
                                'X': this_row.X.values[0],
                                'Y': this_row.Y.values[0],
                                'Z': this_row.Z.values[0]
    }

with open('antuse.json', 'w') as fp:
    json.dump(ants, fp, indent=4)
