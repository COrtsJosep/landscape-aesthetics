import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import plotly.express as px
from dash import Dash, html, dcc
from shapely.geometry import Polygon
from dash.dependencies import Input, Output

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

init_minlat = 33
init_maxlat = 71
init_minlon = -26
init_maxlon = 45

df = (
    pd
    .concat([pd.read_parquet(ns6_chunk_path, columns = columns) for ns6_chunk_path in ns6_chunk_paths])
    .merge(pd.concat([pd.read_csv(ns6_score_path) for ns6_score_path in ns6_score_paths]), on = 'image_path')
    .query(f'gps_map_datum == "WGS-84" and {init_minlat} <= gps_latitude <= {init_maxlat} and {init_minlon} <= gps_longitude <= {init_maxlon}')
    .drop('gps_map_datum', axis = 1)
)
df.loc[:, 'date_time'] = pd.to_datetime(df.loc[:, 'date_time']) # upload date

min_date, max_date = df.loc[:, 'date_time'].min(), df.loc[:, 'date_time'].max()
time_range = max_date - min_date

def get_gdf(bounds, nsteps, time_interval):
    minlat, maxlat, minlon, maxlon = bounds
    low_date, high_date = time_interval
    
    latstepsize = (maxlat - minlat) / nsteps 
    latgrid = np.arange(minlat, maxlat + latstepsize, latstepsize)[:nsteps + 1]
        
    lonstepsize = (maxlon - minlon) / nsteps 
    longrid = np.arange(minlon, maxlon + lonstepsize, lonstepsize)[:nsteps + 1]
    
    df_s = df.loc[(
        (df.loc[:, 'gps_latitude'] >= minlat)
        & (df.loc[:, 'gps_latitude'] <= maxlat)
        & (df.loc[:, 'gps_longitude'] >= minlon)
        & (df.loc[:, 'gps_longitude'] <= maxlon)
        & (df.loc[:, 'date_time'] >= min_date + low_date * time_range)
        & (df.loc[:, 'date_time'] <= min_date + high_date * time_range)
    )].copy()
        
    df_s.loc[:, 'lat_grid'] = ((df_s.loc[:, 'gps_latitude'] - minlat) // latstepsize) * latstepsize + minlat
    df_s.loc[:, 'lon_grid'] = ((df_s.loc[:, 'gps_longitude'] - minlon) // lonstepsize) * lonstepsize + minlon
    
    mat = (
            df_s
            .loc[:, ['lat_grid', 'lon_grid', 'predicted_score']]
            .rename(columns = {'predicted_score': 'Scenicness Score'})
            .groupby(by = ['lat_grid', 'lon_grid']).mean()
            .reset_index()
        )
    
    return gpd.GeoDataFrame(
        mat, 
        geometry = [
            Polygon(((lon, lat), (lon + lonstepsize, lat), (lon + lonstepsize, lat + latstepsize), (lon, lat + latstepsize), (lon, lat)))
            for lon, lat in zip(mat.lon_grid, mat.lat_grid)], 
        crs = 'WGS-84'
    )

app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id = 'scenicness-map'),

    html.Button('Click to update!', id = 'update', n_clicks = 0, 
                style = {
                    'background-color': '#4CAF50',
                    'color': 'white',
                    'padding': '10px 20px',
                    'font-size': '16px',
                    'border': 'none',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'margin-top': '20px',
                    'margin-bottom': '20px'
                }),

    html.Div([
        html.Label('Select a granularity level:', style = {'font-weight': 'bold', 'font-size': '18px'}),
        dcc.Slider(
            10, 100, 5,
            value = 75,
            id = 'granularity_slider',
            marks =  {0: '0', 100: '100'},
            tooltip = {'placement': 'bottom', 'always_visible': True},
            included = True
        )
    ], style = {'margin-bottom': '40px'}),

    html.Div([
        html.Label('Select an opacity level:', style={'font-weight': 'bold', 'font-size': '18px'}),
        dcc.Slider(
            0, 1, step = 0.05,
            value = 0.35,
            id = 'opacity_slider',
            marks = {0: '0%', 0.5: '50%', 1: '100%'},
            tooltip = {'placement': 'bottom', 'always_visible': True},
            included = True
        )
    ], style = {'margin-bottom': '40px'}),

    html.Div([
        html.Label('Select an upload date range:', style={'font-weight': 'bold', 'font-size': '18px'}),
        dcc.RangeSlider(
            0, 1, step = 0.05,
            value = [0, 1],
            id = 'time_interval_slider',
            marks = {0: str(min_date), 0.5: str(min_date + time_range/2), 1: str(max_date)}, 
            included = True
        )
    ], style = {'margin-bottom': '40px'})
    
], style = {
    'font-family': 'Arial, sans-serif',
    'padding': '20px',
    'max-width': '800px',
    'margin': 'auto',
    'background-color': '#f9f9f9',
    'border-radius': '10px',
    'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
})

@app.callback(
    Output('scenicness-map', 'figure'),
    [Input('update', 'n_clicks'), 
     Input('scenicness-map', 'relayoutData'),
     Input('granularity_slider', 'value'),
     Input('opacity_slider', 'value'),
     Input('time_interval_slider', 'value')
    ],
    prevent_initial_call = False
)
def update_map(n_clicks, relayout_data, nsteps, opacity, time_interval):
    
    if relayout_data and 'map._derived' in relayout_data and 'coordinates' in relayout_data['map._derived']:
        minlon, maxlat = relayout_data['map._derived']['coordinates'][0]
        maxlon, minlat = relayout_data['map._derived']['coordinates'][2]
    else:      
        minlat = 33
        maxlat = 71
        minlon = -26
        maxlon = 45

    bounds = (minlat, maxlat, minlon, maxlon)

    gdf = get_gdf(bounds, nsteps, time_interval)

    fig = px.choropleth_map(gdf, 
                            geojson = gdf.geometry, 
                            locations = gdf.index, 
                            color = 'Scenicness Score',
                            center = {'lat': (minlat + maxlat) / 2, 'lon': (minlon + maxlon) / 2},
                            map_style = 'light',
                            color_continuous_scale = 'rainbow',
                            opacity = opacity,
                            zoom = relayout_data['map.zoom'] if relayout_data and 'map.zoom' in relayout_data else 3,
                            height = 700,
                            width = 1000)

    return fig

if __name__ == '__main__':
    app.run_server(debug = False, port = 1070)