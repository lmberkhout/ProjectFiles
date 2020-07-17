import json
import matplotlib.pyplot as plt

with open('antuse.json', 'r') as fp:
    data = json.load(fp)

dates = ['20201001', '20201101', '20201201', '20210101', '20210201', '20210301']
dates.reverse()

for this_date in dates:
    x = []
    y = []
    for loc in data[this_date].values():
        x.append(loc['easting'])
        y.append(loc['northing'])
    plt.plot(x, y, 'o', label=this_date)
plt.legend()
