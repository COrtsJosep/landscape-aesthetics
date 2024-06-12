import time
import shapely
import geopandas
import numpy as np
import pandas as pd
from tqdm import tqdm 
from pathlib import Path
import wikimap_api_helpers
from matplotlib import pyplot as plt

# Very similar to wikimap_api_caller.py - please check comments there.
# The difference here is that we only want to call the API at points where the API (should 
# have returned values but) did not return any results.
# The strategy here is loading the results of the API calling, and seeing if there are lat-lons
# of the grid where we would have expected results, but we have no record of the API returning
# anything.
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
shapefile_path = project_base_path / 'data' / 'external' / 'geoshapes' / 'country_geoshapes.shx'
responses_path = project_base_path / 'data' / 'interim' / 'wikimap_toolforge'

geo_df = (
    geopandas
    .read_file(shapefile_path)
    .query('LEVL_CODE == 0')
    .reset_index()
)

radius = 10000

for _, row in geo_df.iterrows():
    country = row['NUTS_ID']
    shape = wikimap_api_helpers.crop_overseas(row['geometry'])
    
    # load the responses we have gotten so far. since each csv corresponds to a successful API call, all rows
    # of a single csv have the same values for the columns query_lon and query_lat, so we only need to load
    # the first row :)
    # assessed_coordinates is just the info in a list form.
    df_responses = pd.concat([pd.read_csv(path, nrows = 1) for path in (responses_path / country / 'ns0').glob('*.csv')])
    assessed_coordinates = [(row['query_lat'], row['query_lon']) for _, row in df_responses.loc[:, ['query_lat', 'query_lon']].drop_duplicates().iterrows()]
    del df_responses
    
    lats, lons, mask = wikimap_api_helpers.get_query_points(shape)
    for lat, lon, relevant_point in tqdm(zip(lats, lons, mask), desc = country, total = len(lats)):
        if relevant_point:
            # here is the difference with wikimap_api_caller.py:
            # at each grid point, we create a circle of (almost) full radius. Then we check if
            # we have any results that were queried inside of that circle.
            # If not, then the point is empty.
            circle = wikimap_api_helpers.generate_circle(shapely.Point(lon, lat), radius = 7500)
            is_empty = True

            for assessed_lat, assessed_lon in assessed_coordinates:
                if shapely.contains_xy(circle, assessed_lon, assessed_lat):
                    is_empty = False
                    break

            if is_empty: # if it is empty, we want to query it again.
                i = wikimap_api_helpers.get_highest_id(country) + 1
                wikimap_api_helpers.query_at(lat, lon, radius, i, country)
                time.sleep(2.5)

    time.sleep(60*15)