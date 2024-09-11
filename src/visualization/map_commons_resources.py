import glob
import datetime
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_wiki_paths = glob.glob(str(project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'ns6_*.parquet'))
output_path = project_base_path / 'reports' / 'figures'

df = pd.concat([
    pd
    .read_parquet(ns6_wiki_path, columns = ['image_path', 'gps_latitude', 'gps_longitude'])
    for ns6_wiki_path in ns6_wiki_paths
])

df.loc[:, 'download_status'] = df.loc[:, 'image_path'].apply(lambda x: x if 'Not Downloaded' in x else 'Downloaded')
df = (
    df
    .query('download_status == "Downloaded"')
    .loc[:, ['gps_latitude', 'gps_longitude']]
    .astype(float)
    .dropna()
    .drop_duplicates()
)

plt.figure(figsize = (15, 8))
m = Basemap(projection = 'mill', # other projections: https://matplotlib.org/basemap/stable/users/mapsetup.html
            llcrnrlat = 33,
            urcrnrlat = 71,
            llcrnrlon = -26,
            urcrnrlon = 40,
            resolution = 'i')

m.drawcoastlines()
m.drawcountries()

m.scatter(x = df.loc[:, 'gps_longitude'], 
          y = df.loc[:, 'gps_latitude'], 
          s = 0.001, 
          marker = 'x',
          c = 'deepskyblue',
          latlon = True)

plt.title(f'Geolocated Images')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.savefig(output_path / f'map_images_{timestamp}.pdf', 
            bbox_inches = 'tight')
plt.savefig(output_path / f'map_images_{timestamp}.png', 
            bbox_inches = 'tight')
plt.show()