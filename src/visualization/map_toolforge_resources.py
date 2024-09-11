import datetime
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap

valid_input = False
while not valid_input:
    ns_type = input('Select an ns_type. Options are "ns0" and "ns6": ')
    valid_input = (ns_type in ('ns0', 'ns6'))

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
toolforge_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / f'{ns_type}.parquet'
output_path = project_base_path / 'reports' / 'figures'

df = (
    pd
    .read_parquet(toolforge_parquet_path)
    .loc[:, ['resource_lat', 'resource_lon']]
    .drop_duplicates()
)

m = Basemap(projection = 'mill', # other projections: https://matplotlib.org/basemap/stable/users/mapsetup.html
            llcrnrlat = 33,
            urcrnrlat = 71,
            llcrnrlon = -26,
            urcrnrlon = 40,
            resolution = 'i')

m.drawcoastlines()
m.drawcountries()

m.scatter(x = df.loc[:, 'resource_lon'], 
          y = df.loc[:, 'resource_lat'], 
          s = 0.001, 
          marker = 'x',
          c = 'deepskyblue',
          latlon = True)

plt.title(f'Geolocated {ns_type} Resources')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.savefig(output_path / f'map_{ns_type}_resources_{timestamp}.pdf', 
            bbox_inches = 'tight')
plt.savefig(output_path / f'map_{ns_type}_resources_{timestamp}.png', 
            bbox_inches = 'tight')
plt.show()