import pandas as pd
import hvplot.pandas
import colorcet as cc
import holoviews as hv
import datashader as ds
from pathlib import Path
import holoviews.operation.datashader as hd

hv.output(backend = "bokeh")

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_chunk_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'clean').glob('ns6_clean_*.parquet')
ns6_score_paths = (project_base_path / 'data' / 'processed' / 'landscape_score').glob('processed_ns6_clean_*.csv')

columns = [
 'gps_latitude',
 'gps_longitude',
 'gps_map_datum',
 'image_path'
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
df.loc[:, 'x'], df.loc[:, 'y'] = ds.utils.lnglat_to_meters(df.loc[:, 'gps_longitude'], df.loc[:, 'gps_latitude'])

density_canvas = hv.element.tiles.CartoDark().opts(
    alpha = 0.75, 
    width = 800, 
    height = 740, 
    bgcolor = 'black'
)

density_points = hd.datashade(
    hv.Points(df, ['x', 'y']), 
    cmap = cc.fire
).opts(xlabel = 'Longitude', 
       ylabel = 'Latitude')

density_scatterplot = density_canvas * density_points
density_scatterplot