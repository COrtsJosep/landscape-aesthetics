import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
metadata_path = project_base_path / 'data' / 'external' / 'scenicornot' / 'scenicornot.metadata.csv'
grid_path = project_base_path / 'data' / 'external' / 'scenicornot' / 'gridimage_base.tsv'
output_path = project_base_path / 'reports' / 'figures'

gridimage_ids = pd.read_csv(metadata_path, usecols = ['gridimage_id']).loc[:, 'gridimage_id']

df = (
    pd
    .read_csv(grid_path, sep = '\t', usecols = ['gridimage_id', 'wgs84_lat', 'wgs84_long'])
)
df = df.loc[df.loc[:, 'gridimage_id'].isin(gridimage_ids), ['wgs84_lat', 'wgs84_long']].dropna().drop_duplicates()

plt.figure(figsize = (15, 8))
m = Basemap(projection = 'mill', # other projections: https://matplotlib.org/basemap/stable/users/mapsetup.html
            llcrnrlat = 49,
            urcrnrlat = 61,
            llcrnrlon = -9,
            urcrnrlon = 4,
            resolution = 'i')

m.drawcoastlines()
m.drawcountries()

m.scatter(x = df.loc[:, 'wgs84_long'], 
          y = df.loc[:, 'wgs84_lat'], 
          s = 0.001, 
          marker = 'x',
          c = 'deepskyblue',
          latlon = True)

plt.title(f'Geolocated SoN Images')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

plt.savefig(output_path / f'map_son_images.pdf', 
            bbox_inches = 'tight')
plt.savefig(output_path / f'map_son_images.png', 
            bbox_inches = 'tight')
plt.show()