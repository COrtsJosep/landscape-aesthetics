import re
import math
import time
import json
import shapely
import requests
import pandas as pd
from pathlib import Path
from geopy import distance

def generate_circle(point, radius = 10000):
    '''
    There are two ways of generate the grid of points where to evaluate the API: 
    - either we call the API in points that are in the country, OR 
    - we call the API in points such that the 10KM radius circle and the country have a nonempty intersection. 
    The first way is simple, the second requires a bit of thought, and a function to create a circle from a point. 
    That is the function ```generate_circle(point)```.
    '''
    
    lon_centre, lat_centre = point.bounds[:2] # take the coordinates of the point
    naive_circle = point.buffer(1) # blow it to a circle. this is naive because the circle has now radius 1, but the unit of mesure here is degrees, not KM...
    lon_max, lat_max = naive_circle.bounds[2:] # take the extrema of the circle in the x and y directions
    
    lat_scaling_factor = distance.geodesic((lat_centre, lon_centre), (lat_max, lon_centre)).m # scalar s.t. the distance from centre to top of the circle is 1M
    
    correct_lat_circle = point.buffer(radius/lat_scaling_factor) # correct it. now the "circle" is an ellipsis on the degree space 
    
    lon_scaling_factor = distance.geodesic((lat_centre, lon_centre), (lat_centre, lon_max)).m # scalar s.t. the distance from centre to side of ellipsis is 1M
    latitude_correction = (1-(1.0508906983730856)**-1)*(52.3938**-2)*(lat_centre**2) + (1.0508906983730856)**-1 # trust me guys
    
    correct_circle = shapely.affinity.scale(correct_lat_circle, 
                                            radius * latitude_correction * math.log(lon_scaling_factor)/lon_scaling_factor, 
                                            1)
    return correct_circle

def get_query_points(shape, use_circles = True, radius = 10000):
    '''
    The following procedure generates the grid of points where we should call the API. How it works: 
    - It begins at the southernmost, westmost point of the box that encloses the country. 
    - Then takes 10KM steps towards the east. At each step evaluates if the point is in the country (alternatively, 
        if its corresponding circle intersects the country). 
    - When the procedure steps too far away into the east, out of the box that contains the country, then 
        it returns to the westernmost point, but 10KM to the north of it. 
    - Then begins the walk eastwards again. 
    - This is repeated until the procedure oversteps the northernmost, eastmost corner of the box.
    '''
    
    lon, lat = shape.bounds[:2]
    lons, lats, mask = [], [], []

    indent = True
    while lat < shape.bounds[3]:
        while lon < shape.bounds[2]:
            point = shapely.geometry.Point(lon, lat)
            lats.append(lat); lons.append(lon)
            if use_circles:
                mask.append(shape.intersects(generate_circle(point, radius = radius)))
            else:
                mask.append(shape.contains(point))
            
            lat, lon, _ = distance.geodesic(meters = radius*3**0.5).destination((lat, lon), bearing = 90)
        
        lon = shape.bounds[0]
        if indent:
            lat, lon, _ = distance.geodesic(meters = 0.5*radius*3**0.5).destination((lat, lon), bearing = 90)
        lat, lon, _ = distance.distance(meters = 3*radius/2).destination((lat, lon), bearing = 0)
        
        indent = not indent

    return lats, lons, mask

def preprocess_json(json):
    '''
    Takes the JSON (a list of dictionaries, in this case) given by the API call, and unpacks
    nested lists inside of it.
    Fields that have nested lists (or dicts) are coordinates, imageinfo, and entityterms.
    '''    
    for item in json: # coordinates manipulation
        multiple_coordinates = False
        if 'coordinates' in item.keys():
            if type(item['coordinates']) == list:
                multiple_coordinates = len(item['coordinates']) > 1
                item['coordinates'] = item['coordinates'][0]
            elif type(item['coordinates']) == dict:
                multiple_coordinates = len(item['coordinates'].keys()) > 1
                item['coordinates'] = item['coordinates'][list(item['coordinates'].keys())[0]]
            else:
                print('Nonstandard coordinates:', item['coordinates'])
        item['multiple_coordinates'] = multiple_coordinates

    for item in json: # imageinfo manipulation
        multiple_imageinfo = False
        if 'imageinfo' in item.keys():
            if type(item['imageinfo']) == list:
                multiple_imageinfo = len(item['imageinfo']) > 1
                item['imageinfo'] = item['imageinfo'][0]
            elif type(item['imageinfo']) == dict:
                multiple_imageinfo = len(item['imageinfo'].keys()) > 1
                item['imageinfo'] = item['imageinfo'][list(item['imageinfo'].keys())[0]]
            else:
                print('Nonstandard image information:', item['imageinfo'])
        item['multiple_imageinfo'] = multiple_imageinfo

    for item in json: # label manipulation
        multiple_labels = False
        if 'entityterms' in item.keys():
            if 'label' in item['entityterms'].keys():
                if type(item['entityterms']['label']) == list:
                    multiple_labels = len(item['entityterms']['label']) > 1
                    item['entityterms']['label'] = ';'.join(item['entityterms']['label'])
                else:
                    print('Nonstandard entry label:', item['entityterms']['label'])
        item['multiple_labels'] = multiple_labels
    
    return json

def crop_overseas(shape):
    ''' 
    Crops islands and overseas territories from a shapely multipolygon.
    Having territories very far away from the mainland kind of mess with 
    the grid generating algorithm.
    '''
    if type(shape) == shapely.geometry.MultiPolygon:
        newshape_list = []
        for geom in list(shape.geoms):
            if not (geom.centroid.y < 34 or (geom.centroid.y < 43 and geom.centroid.x < -11.5)):
                newshape_list.append(geom)
        shape = shapely.geometry.MultiPolygon(newshape_list)

    return shape

def get_highest_id(country):
    '''
    Given a country code, returns the maximum query ID executed (which returned)
    results for that country.
    '''
    file_location_path = Path(__file__)
    project_base_path = file_location_path.parent.parent.parent
    country_path = project_base_path / 'data' / 'interim' / 'wikimap_toolforge' / country

    ns_type_max = []
    for ns_type in [path.name for path in country_path.glob('*')]:
        csv_name_list = [path.name for path in (country_path / ns_type).glob('*.csv')]
        ns_type_max.append(
            max([int(re.search(r'id(\d+)_', name).groups()[0]) for name in csv_name_list])
        )

    return max(ns_type_max)

def query_at(lat, lon, radius, i, country):
    '''
    This function calls the api at the specified coordinates. If there are too many results, then the function
    calls itself on four smaller regions.
    For each successful call, a raw version of the data is stored as a JSON, and a cleaner version (with some
    data left out) is stored as a csv table.
    '''
    
    time.sleep(7.5) # one request every 7.5 seconds max
    
    headers = {
        'User-Agent': 'API Caller - please do not block us - send us a message!' ,
        'From': 'josep.cunqueroorts@uzh.ch'
    }
    query_string = f'https://wikimap.toolforge.org/api.php?wp=false&cluster=false&dist={radius}&lat={lat}&lon={lon}&commons&allco=true&project=wikidata'

    responded = False
    times_slept = 0
    while not responded or response.status_code != 200:
        try:
            response = requests.get(query_string, headers = headers, timeout = 60)
            responded = True
        except Exception as e:
            print(f'Got exception {e} at coordinates({round(lat, 2)}, {round(lon, 2)}). Waiting {5*times_slept} seconds and then trying again.') 
            responded = False
            
        if responded and response.status_code != 200:
            print(f'Got code {response.status_code} at coordinates({round(lat, 2)}, {round(lon, 2)}). Waiting {5*times_slept} seconds and then trying again.') 
        
        time.sleep(5*times_slept)
        if times_slept > 5:
            input('Temporarily stopped. Press any key to resume: ')
        times_slept += 1
        
    n = len(response.json())
    if n == 0:
        return i
        
    elif n > 800:
        new_radius = int(radius / 2)
        for j in range(4):
            new_lat, new_lon, _ = distance.geodesic(meters = new_radius).destination((lat, lon), bearing = 45+j*90)
            i = query_at(lat = new_lat, lon = new_lon, radius = new_radius, i = i, country = country)

        return i
        
    else:
        file_location_path = Path(__file__)
        project_base_path = file_location_path.parent.parent.parent

        raw_json_location_path = project_base_path / 'data' / 'raw' / Path(f'wikimap_toolforge/{country}')
        raw_json_path = raw_json_location_path / Path(f'{country}_id{i}.json') 

        raw_json_location_path.mkdir(parents = True, exist_ok = True)
        raw_json = response.json()
        with open(raw_json_path, 'w') as file:
            json.dump(raw_json, file)
        
        preprocessed_json = preprocess_json(raw_json)
        for ns_type in set([item['ns'] for item in preprocessed_json]):
            df = (
                pd
                .json_normalize([item for item in preprocessed_json if item['ns'] == ns_type])
                .assign(query_lat = lat,
                        query_lon = lon,
                        radius = radius,
                        query_id = i,
                        country = country
                       )
            )

            df_location_path = project_base_path / 'data' / 'interim' / Path(f'wikimap_toolforge/{country}/ns{ns_type}')
            df_path = df_location_path / Path(f'{country}_id{i}_ns{ns_type}.csv') 

            df_location_path.mkdir(parents = True, exist_ok = True)
            df.to_csv(df_path, index = False)

        return i + 1