import json
import requests
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

def transform_image(image_path):
    # transform the image, as in: rescale, crop, convert to grayscale, convert to jpeg... to be decided
    ...
    new_image_path = image_path
    return new_image_path

def download_image(url, country, ns_type, query_id, title, headers):
    '''
    Downloads an image at a path determined by the attributes of the image.
    '''
    resource_destination = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'images' / country / ns_type / str(query_id) / title
    resource_destination.parent.mkdir(parents = True, exist_ok = True)
    
    try:
        request = requests.get(url, headers = headers)
        with open(resource_destination, 'wb') as f:
            f.write(request.content)
        resource_location = transform_image(resource_destination)
        return str(resource_location.relative_to(project_base_path))
    except Exception as e:
        print(e, 'at', url)
        return None

def store_metadata(metadata, country, ns_type, query_id, title):
    '''
    Stores image metadata at a path determined by the attributes of the image, as a json.
    '''
    metadata_destination = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'metadata' / country / ns_type / str(query_id) / title
    metadata_destination = metadata_destination.with_suffix('.json')
    metadata_destination.parent.mkdir(parents = True, exist_ok = True)

    try:   
        with open(metadata_destination, 'w') as file:
                json.dump(metadata, file)
        return str(metadata_destination.relative_to(project_base_path))
    except Exception as e:
        print(e, 'at', title)
        return None