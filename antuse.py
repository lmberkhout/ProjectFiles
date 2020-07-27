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
new_nodes['20210201'] = ['N16', 'N11']
new_nodes['20210301'] = ['N06', 'N17']
new_nodes['20210401'] = ['N06', 'N17']
new_nodes['20210501'] = ['N21', 'N22']
new_nodes['20210601'] = ['N23', 'N24']
new_nodes['20210701'] = ['N25', 'N26']
new_nodes['20210801'] = ['N27', 'N28', 'N29']

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


this_date = '20210801'

rest_of_em = {
              'HB346':	[540762.90, 6601530.14, 1048.22],
              'HB347':	[540908.90, 6601530.14, 1048.44],
              'HB348':	[541054.90, 6601530.14, 1048.79],
              'HB349':	[541200.90, 6601530.14, 1049.28],
              'HB341':	[540689.90, 6601412.13, 1049.05],
              'HA342':	[540835.90, 6601403.70, 1049.38],
              'HA343':	[540981.90, 6601403.70, 1049.54],
              'HA344':	[541127.90, 6601403.70, 1049.86],
              'HB345':	[541273.90, 6601403.70, 1050.33],
              'HB337':	[540616.90, 6601285.69, 1050.21],
              'HA338':	[540762.90, 6601285.69, 1050.38],
              'HA339':	[541200.90, 6601277.26, 1050.96],
              'HB340':	[541346.90, 6601277.26, 1051.45],
              'HB333':	[540543.90, 6601159.25, 1051.37],
              'HA334':	[540689.90, 6601159.25, 1051.58],
              'HA335':	[541273.90, 6601167.68, 1051.93],
              'HB336':	[541419.90, 6601167.68, 1052.46],
              'HB329':	[540616.90, 6601032.81, 1053.22],
              'HA330':	[540762.90, 6601032.81, 1053.08],
              'HA331':	[541200.90, 6601041.24, 1052.62],
              'HB332':	[541346.90, 6601041.24, 1053.12],
              'HB324':	[540689.90, 6600906.37, 1054.56],
              'HA325':	[540835.90, 6600906.37, 1054.50],
              'HA326':	[540981.90, 6600914.80, 1054.07],
              'HA327':	[541127.90, 6600914.80, 1053.90],
              'HB328':	[541273.90, 6600914.80, 1053.65],
              'HB320':	[540762.90, 6600779.93, 1056.13],
              'HB321':	[540908.90, 6600788.36, 1055.37],
              'HB322':	[541054.90, 6600788.36, 1055.08],
              'HB323':	[541200.90, 6600788.36, 1055.08]}

this_node = 'N12'
for stn_name, position in rest_of_em.items():
    this_stn = int(stn_name[2:])
    ants[this_date][this_stn] = {
                                'node': this_node,
                                'easting': position[0],
                                'northing': position[1],
                                'latitude': 0.0,
                                'longitude': 0.0,
                                'elevation': position[2],
                                'X': 0.0,
                                'Y': 0.0,
                                'Z': 0.0
    }

with open('antuse.json', 'w') as fp:
    json.dump(ants, fp, indent=4)
