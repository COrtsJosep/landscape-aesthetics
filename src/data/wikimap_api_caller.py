import time
import geopandas
from tqdm import tqdm 
from pathlib import Path
import wikimap_api_helpers

# first define the path structure
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
shapefile_path = project_base_path / 'data' / 'external' / 'geoshapes' / 'country_geoshapes.shx'

# load the file with the geoshapes of each country
geo_df = (
    geopandas
    .read_file(shapefile_path)
    .query('LEVL_CODE == 0')
    .reset_index()
)
    
radius = 10000

# simple as: iterate over all countries...
for _, row in geo_df.iterrows():
    country = row['NUTS_ID']
    shape = wikimap_api_helpers.crop_overseas(row['geometry']) # ... load the geoshape ...

    i = 0
    lats, lons, mask = wikimap_api_helpers.get_query_points(shape) # ... generate the grid of lats and lons to evaluate ...
    for lat, lon, relevant_point in tqdm(zip(lats, lons, mask), desc = country, total = len(lats)):
        if relevant_point: # ... check if the lat-lon is inside of the geoshape ...
            i = wikimap_api_helpers.query_at(lat, lon, radius, i, country) # ... and evaluate!

    time.sleep(60*15) # Sleep after finishing a country.