import json
import matplotlib.pyplot as plt

with open('antuse.json', 'r') as fp:
    data = json.load(fp)

dates = ['20201001', '20201101', '20201201', '20210101', '20210201', '20210301']
dates += ['20210401', '20210501', '20210601', '20210701']
dates.reverse()

color_list = ['b', 'g', 'r', 'c', 'm', 'k', 'tab:blue', 'tab:orange', 'tab:brown', 'tab:olive',
              'tab:pink', 'bisque', 'lightcoral', 'goldenrod', 'lightgrey', 'lime', 'lightseagreen']

for clr, this_date in enumerate(dates):
    x = []
    y = []
    for loc in data[this_date].values():
        x.append(loc['easting'])
        y.append(loc['northing'])
    plt.plot(x, y, 'o', color=color_list[clr], label=this_date)
plt.legend()
