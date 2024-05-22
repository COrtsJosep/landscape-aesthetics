import math
import time
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
                mask.append(shape.intersects(generate_circle(point)))
            else:
                mask.append(shape.contains(point))
            
            lat, lon, _ = distance.geodesic(meters = radius*3**0.5).destination((lat, lon), bearing = 90)
        
        lon = shape.bounds[0]
        if indent:
            lat, lon, _ = distance.geodesic(meters = 0.5*radius*3**0.5).destination((lat, lon), bearing = 90)
        lat, lon, _ = distance.distance(meters = 3*radius/2).destination((lat, lon), bearing = 0)
        
        indent = not indent

    return lats, lons, mask

def query_at(lat, lon, radius, i, country):
    '''
    This function calls the api at the specified coordinates. If there are too many results, then the function
    calls itself on four smaller regions.
    '''
    
    time.sleep(2)
    
    query_string = f'https://wikimap.toolforge.org/api.php?wp=false&cluster=false&dist={radius}&lat={lat}&lon={lon}&commons&allco=true&project=wikidata'
    response = requests.get(query_string)
    times_slept = 0
    while response.status_code != 200:
        print(f'Got code {response.status_code} at coordinates({round(lat, 2)}, {round(lon, 2)}). Waiting {2*times_slept} seconds and then trying again.') 
        time.sleep(2*times_slept)
        times_slept += 1
        response = requests.get(query_string)

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
        for ns_type in set([item['ns'] for item in response.json()]):
            df = (
                pd
                .DataFrame
                .from_dict(pd.json_normalize([item for item in response.json() if item['ns'] == ns_type]),
                           orient='columns')
                .assign(query_lat = lat,
                        query_lon = lon,
                        radius = radius)
            )

            file_location_path = Path(__file__)
            project_base_path = file_location_path.parent.parent.parent
            location_path = project_base_path / 'data' / 'interim' / Path(f'wikimap_toolforge/{country}/ns{ns_type}')
            file_path = location_path / Path(f'{country}_id{i}_ns{ns_type}.csv') 

            location_path.mkdir(parents = True, exist_ok = True)
            df.to_csv(file_path, index = False)

        return i + 1