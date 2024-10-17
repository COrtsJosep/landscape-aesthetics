import numpy as np
import pandas as pd
from pathlib import Path
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

nsteps = 100

latstepsize = (maxlat - minlat) / nsteps 
latgrid = np.arange(minlat, maxlat + latstepsize, latstepsize)[:nsteps + 1]

lonstepsize = (maxlon - minlon) / nsteps 
longrid = np.arange(minlon, maxlon + lonstepsize, lonstepsize)[:nsteps + 1]

df.loc[:, 'lat_grid'] = ((df.loc[:, 'gps_latitude'] - minlat) // latstepsize) * latstepsize + minlat
df.loc[:, 'lon_grid'] = ((df.loc[:, 'gps_longitude'] - minlon) // lonstepsize) * lonstepsize + minlon

mat = (
    df
    .loc[:, ['lat_grid', 'lon_grid', 'predicted_score']]
    .rename(columns = {'predicted_score': 'scenicness'})
    .groupby(by = ['lat_grid', 'lon_grid']).mean()
    .reset_index()
    .pivot(index = 'lat_grid', columns = 'lon_grid', values = 'scenicness')
)

fig = plt.figure(figsize=(12,12))
ax = fig.add_axes([0.1,0.1,0.8,0.8])

m = Basemap(projection = 'mill', # other projections: https://matplotlib.org/basemap/stable/users/mapsetup.html
            llcrnrlat = minlat,
            urcrnrlat = maxlat,
            llcrnrlon = minlon,
            urcrnrlon = maxlon,
            resolution = 'i')

m.drawcoastlines()
m.drawcountries()

x, y = m(*np.meshgrid(mat.columns, mat.index))

cs = m.contourf(x = x, y = y, data = mat, cmap = cm.GMT_seis, levels = 4)
cbar = m.colorbar(cs, location = 'bottom', pad = "5%")
cbar.set_label('Average Scenicness Score')
plt.show()