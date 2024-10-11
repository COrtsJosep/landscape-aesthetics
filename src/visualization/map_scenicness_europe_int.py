import geopandas as gpd
import pandas as pd
#import h3
import numpy as np
from shapely.geometry import Point
import plotly.express as px
from dash import Dash, html, dcc
#import dash_leaflet as dl
from dash.dependencies import Input, Output
###########################################
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
###########################################
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
#############################################
nsteps = 50

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
        #.pivot(index = 'lat_grid', columns = 'lon_grid', values = 'scenicness')
    )

gdf = geopandas.GeoDataFrame(
    mat, 
    geometry = [Polygon(((lon, lat), (lon + lonstepsize, lat), (lon + lonstepsize, lat + latstepsize), (lon, lat + latstepsize), (lon, lat))) for lon, lat in zip(mat.lon_grid, mat.lat_grid)], 
    crs="WGS-84"
)

fig = px.choropleth_map(gdf, geojson=gdf.geometry, locations=gdf.index, color="scenicness")
fig.show()

fig = px.choropleth_map(gdf, 
                        geojson=gdf.geometry, 
                        locations=gdf.index, 
                        color="scenicness",
                        center={"lat": 46.948056, "lon": 7.4475},
                        map_style="carto-positron",
                        color_continuous_scale = 'Cividis',
                        opacity = 0.75,
                        zoom=3,
                       height = 700,
                       width = 1000)
fig.show()

#############################################
# Initialize Dash app
app = Dash(__name__)

# Layout with map and zoom slider
app.layout = html.Div([
    dcc.Graph(id="gdp-map"),
    dcc.Slider(id="zoom-slider", min=1, max=10, value=1)  # Simulated zoom level
])

# Function to generate 100x100 grid and calculate average GDP per capita
def get_data(bounds, nsteps = 100):
    minlat, minlon, maxlat, maxlon = bounds
    
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

    return mat

# Callback to update grid based on zoom level and bounds
import plotly.graph_objects as go

# Initialize the Dash app
# Define the layout with map
app.layout = html.Div([
    dcc.Graph(id="gdp-map"),
])

# Function to generate a grid and calculate average GDP per capit
# Callback to update the contour plot based on the map bounds
@app.callback(
    Output("gdp-map", "figure"),
    [Input("gdp-map", "relayoutData")]
)
def update_map(relayout_data):
    # Default world bounds
    minlat = 33
    maxlat = 71
    minlon = -26
    maxlon = 45
    bounds = (minlat, minlon, maxlat, maxlon)
    
    # Check if relayout_data has mapbox bounds information
    if relayout_data and "mapbox._derived" in relayout_data:
        derived = relayout_data["mapbox._derived"]
        if "coordinates" in derived:
            # Extract bounds (min_lon, min_lat, max_lon, max_lat)
            minlon, minlat = derived["coordinates"][0]
            maxlon, maxlat = derived["coordinates"][2]
            bounds = (minlat, minlon, maxlat, maxlon)

    # Generate the grid and get average GDP per capita
    matrix = get_data(bounds, nsteps = 100)
    lat_bins = matrix.index.to_numpy()
    lon_bins = matrix.columns.to_numpy()
    grid_data = matrix.to_numpy()
    
    # Create the figure with go.Contour
    fig = go.Figure(go.Scattermap(
    mode = "lines", fill = "toself",
    lon = [],
    lat = []))

    # Add contour plot to figure

    # Update the map layout with Mapbox
    """"
    fig.update_layout(
        map=dict(
            style="carto-positron",
            center=dict(lat=(bounds[0] + bounds[2]) / 2, lon=(bounds[1] + bounds[3]) / 2),
            zoom=3,  # Initial zoom level can be overridden later
        ),
        map_layers=[{
            "below": 'traces',
            "sourcetype": "raster",
            "source": ["https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"]
        }],
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600
    )"""

    fig.add_trace(go.contour(
        z=grid_data,
        x=lon_bins,  # Longitude bins (x-axis)
        y=lat_bins,  # Latitude bins (y-axis)
        colorscale='Viridis',
        contours_coloring='heatmap',
        colorbar_title='GDP per Capita',
        opacity = 0.5
        #zmin=1000, zmax=50000
    ))

    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, port=1070)
