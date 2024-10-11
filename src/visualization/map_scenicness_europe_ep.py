import numpy as np
import pandas as pd
from pathlib import Path
from tqdm.contrib import tenumerate
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap, cm

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_chunk_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'clean').glob('ns6_clean_*.parquet')
ns6_score_paths = (project_base_path / 'data' / 'processed' / 'landscape_score').glob('processed_ns6_clean_*.csv')
output_path = project_base_path / 'reports' / 'figures'

columns = [
 'date_time',
 'gps_latitude',
 'gps_longitude',
 'gps_map_datum',
 'image_path',
 'date_time_original'
]

minlat = 33
maxlat = 71
minlon = -26
maxlon = 45

df = (
    pd
    .concat([pd.read_parquet(ns6_chunk_path, columns = columns) for ns6_chunk_path in ns6_chunk_paths])
    .merge(pd.concat([pd.read_csv(ns6_score_path) for ns6_score_path in ns6_score_paths]), on = 'image_path')
    .query(f'gps_map_datum == "WGS-84" and {minlat} <= gps_latitude <= {maxlat} and {minlon} <= gps_longitude <= {maxlon}')
    .drop('gps_map_datum', axis = 1)
)

nsteps = 200

latstep = (maxlat - minlat) / nsteps 
lonstep = (maxlon - minlon) / nsteps 

step = min(latstep, lonstep)

latgrid = np.arange(minlat, maxlat + step, step)
latgrid = latgrid[latgrid <= maxlat]
lat_centers = (latgrid[:-1] + latgrid[1:]) / 2
longrid = np.arange(minlon, maxlon + step, step)
longrid = longrid[longrid <= maxlon]
lon_centers = (longrid[:-1] + longrid[1:]) / 2

mat = np.zeros((len(latgrid) - 1, len(longrid) - 1))
for i, clat in tenumerate(lat_centers):
    for j, clon in enumerate(lon_centers):
        df.loc[:, 'u'] = np.sqrt((df.loc[:, 'gps_latitude'] - clat) ** 2 + (df.loc[:, 'gps_longitude'] - clon) ** 2) / 1
        df_u = df.loc[df.loc[:, 'u'] <= 1]
        mat[i, j] = (df_u.loc[:, 'predicted_score'] * df_u.loc[:, 'u']).sum() / df_u.loc[:, 'u'].sum() if not df_u.empty else np.nan

fig = plt.figure(figsize = (12, 12))
ax = fig.add_axes([0.1,0.1,0.8,0.8])

m = Basemap(projection = 'mill', # other projections: https://matplotlib.org/basemap/stable/users/mapsetup.html
            llcrnrlat = minlat,
            urcrnrlat = maxlat,
            llcrnrlon = minlon,
            urcrnrlon = maxlon,
            resolution = 'i')

m.drawcoastlines()
m.drawcountries()

x, y = m(*np.meshgrid(longrid, latgrid))

cs = m.pcolormesh(x = x, y = y, data = mat, cmap = cm.GMT_seis)
cbar = m.colorbar(cs, location = 'bottom', pad = "5%")
cbar.set_label('Average Scenicness Score')
plt.show()