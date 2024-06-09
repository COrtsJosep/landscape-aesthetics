import time
import shapely
import geopandas
import numpy as np
import pandas as pd
from tqdm import tqdm 
from pathlib import Path
import wikimap_api_helpers
from matplotlib import pyplot as plt

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

for _, row in geo_df.iterrows():
    country = row['NUTS_ID']
    shape = wikimap_api_helpers.crop_overseas(row['geometry'])

    country_response_path = responses_path / country
    if country_response_path.exists(): #and country == 'SK':
        df_responses = pd.concat([pd.read_csv(path) for path in (country_response_path / 'ns6').glob('*.csv')])
        assessed_coordinates = [(row['query_lat'], row['query_lon']) for _, row in df_responses.loc[:, ['query_lat', 'query_lon']].drop_duplicates().iterrows()]
        
        is_empty_list = []
        lats, lons, mask = wikimap_api_helpers.get_query_points(shape)
        for lat, lon, relevant_point in tqdm(zip(lats, lons, mask), desc = country, total = len(lats)):
            if relevant_point:
                circle = wikimap_api_helpers.generate_circle(shapely.Point(lon, lat), radius = 7500)
                is_contained_list = [circle.contains(shapely.Point(assessed_lon, assessed_lat)) 
                                    for assessed_lat, assessed_lon in assessed_coordinates]
                is_empty = not any(is_contained_list)
                is_empty_list.append(is_empty)
        empty_prop = round(np.array(is_empty_list).mean(), 3)
        if empty_prop > 0:
            plt.scatter(np.array(lons)[mask],
                np.array(lats)[mask],
                c = is_empty_list)
            plt.suptitle(country)
            plt.title('Prop of empty: ' + str(empty_prop)) 
            plt.show()