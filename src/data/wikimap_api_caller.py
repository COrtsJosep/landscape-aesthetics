import time
import geopandas
from tqdm import tqdm 
from pathlib import Path
import wikimap_api_helpers

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
shapefile_path = project_base_path / 'data' / 'external' / 'geoshapes' / 'country_geoshapes.shx'
geo_df = (
    geopandas
    .read_file(shapefile_path)
    .query('LEVL_CODE == 0')
    .reset_index()
)
    
radius = 10000

for _, row in geo_df.loc[23:].iterrows():
    country = row['NUTS_ID']
    shape = wikimap_api_helpers.crop_overseas(row['geometry'])

    i = 0
    lats, lons, mask = wikimap_api_helpers.get_query_points(shape)
    for lat, lon, relevant_point in tqdm(zip(lats, lons, mask), desc = country, total = len(lats)):
        if relevant_point:
            i = wikimap_api_helpers.query_at(lat, lon, radius, i, country)

    time.sleep(60*15)