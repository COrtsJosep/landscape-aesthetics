import io
import math
import json
import time
import requests
import urllib.parse
import pandas as pd
from PIL import Image
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
headers = {'User-Agent': 'WikimediaCallerBot/1.0 (josep.cunqueroorts@uzh.ch)'}

def acceptable_batch_list(batch_list):
    titles_strings_list = [urllib.parse.quote('|'.join(batch.loc[:, 'title'])) for batch in batch_list]
    size_list = [len(titles_string) for titles_string in titles_strings_list]
    return all([size < 8000 for size in size_list])

def generate_batches(group):
    batch_size = 50
    num_batches = math.ceil(group.shape[0] / batch_size) # in groups of batch_size
    batch_list = [group.loc[(batch_size*i):(batch_size*(i + 1) - 1)] for i in range(num_batches)]
    
    while not acceptable_batch_list(batch_list) and batch_size != 1:
        batch_size = max(batch_size - 5, 1)
        num_batches = math.ceil(group.shape[0] / batch_size) # in groups of batch_size
        batch_list = [group.loc[(batch_size*i):(batch_size*(i + 1) - 1)] for i in range(num_batches)]

    return batch_list

def call_api(url, rest_time, task, params = None):
    time.sleep(rest_time)
    
    responded = False
    times_slept = 0
    while not responded or response.status_code != 200:
        try:
            response = requests.get(url, params = params, headers = headers, timeout = 60)
            print('URL length:', len(response.url))
            responded = True
        except Exception as e:
            print(f'Got exception {e} at task "{task}". Waiting {5*times_slept} seconds and then trying again.') 
            responded = False
            
        if responded and response.status_code != 200:
            print(f'Got code {response.status_code} at task "{task}". Waiting {5*times_slept} seconds and then trying again.') 
        
        time.sleep(5*times_slept)
        if times_slept > 5:
            try:
                print('The response included the following text:', response.text)
            except:
                print('The endpoint never responded.')
            input('Temporarily stopped. Input anything to resume: ')
        times_slept += 1
    
    return response

def center_crop(image):
    '''
    Takes a PIL image as input. Crops it to a square with side length equal
    to the shorter side of the original size, centered at the middle of the 
    image. Returns that.
    '''
    width, height = image.size
    new_side = min(width, height)
    
    left = (width - new_side)/2
    top = (height - new_side)/2
    right = (width + new_side)/2
    bottom = (height + new_side)/2
    
    return image.crop((left, top, right, bottom))


def transform_image(image):
    '''
    Takes a PIL image, transforms it, and returns it. Transformations by now are:
        - center crop,
        - resize to 224x224, and
        - convert to RGB color mode (3 color channels: Red Green Blue).
    '''
    # TO FULLY DECIDE
    # TODO: what if operations fail?
    image = center_crop(image) # center crop (select a square with shorter side)
    image = image.resize((224, 224)) # resize to a 224x224 square
    image = image.convert('RGB') # convert to RGB
    return image

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

def download_image(url, country, ns_type, query_id, title):
    '''
    Downloads an image at a path determined by the attributes of the image.
    '''
    resource_destination = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'images' / country / ns_type / str(query_id) / title
    resource_destination = resource_destination.with_suffix('.jpeg') # whatever it is, it will be converted to jpeg
    resource_destination.parent.mkdir(parents = True, exist_ok = True)

    response = call_api(url = url, rest_time = 0, task = 'fetch image')
    image = Image.open(io.BytesIO(response.content))
    image = transform_image(image)
    image.save(resource_destination)

    return str(resource_destination.relative_to(project_base_path))

def download_batch(batch, ns_type):
    titles_str = '|'.join(batch.loc[:, 'title']) # separate them with |s
    
    api_endpoint = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'prop': 'imageinfo',
        'iiprop': 'url|mediatype|metadata|extmetadata|badfile',
        'titles': titles_str,
        'format': 'json'
    }

    batch_complete = False
    while not batch_complete:
        response = call_api(url = api_endpoint,
                            rest_time = 1,
                            task = 'fetch image data',
                            params = params)
        response_json = response.json()
        batch_complete = ('batchcomplete' in response_json.keys())

    renaming_dict = {title: title for title in batch.loc[:, 'title']}
    if 'normalized' in response_json['query'].keys():
        for element in response_json['query']['normalized']:
            renaming_dict[element['to']] = element['from']
        # TODO
        # some file titles had to be normalized. see why or just record the title change
        #print('Titles were normalized. See:', response_json['query']['normalized'])
            
    pages_dct = response_json['query']['pages']
    pages_list = [pages_dct[key] for key in pages_dct.keys()]
    cleaned_pages_list = []
    
    for page in pages_list: # write documentation
        normalized_title = page['title']
        unnormalized_title = renaming_dict[normalized_title]
        page['normalized_title'] = normalized_title
        page['unnormalized_title'] = unnormalized_title
        
        query_id = batch.loc[batch.loc[:, 'title'] == unnormalized_title, 'query_id'].item()
        country = batch.loc[batch.loc[:, 'title'] == unnormalized_title, 'country'].item()
        
        metadata = {dct['name']: dct['value'] for dct in page['imageinfo'][0]['metadata']}
        
        page['imageinfo'][0]['extmetadata']
        for key in page['imageinfo'][0]['extmetadata'].keys():
            page[key] = page['imageinfo'][0]['extmetadata'][key]['value']
            # TODO: further parse results which are unpretty?

        page['url'] = page['imageinfo'][0]['url']
        page['mediatype'] = page['imageinfo'][0]['mediatype']
        page['explicit_content'] = 'yes' if 'badfile' in page['imageinfo'][0].keys() else None
        page['metadata_path'] = store_metadata(metadata = metadata,                                                   
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = unnormalized_title
        )
        page['image_path'] = download_image(url = page['url'], 
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = unnormalized_title
        )
        del page['title']
        del page['imageinfo']

        cleaned_pages_list.append(page)       
    
    df_destination = (
        project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'dataframes' 
        / country / ns_type / f'{country}_id{query_id}_{ns_type}.csv' 
    )
    df_destination.parent.mkdir(parents = True, exist_ok = True)
    
    existing_df = pd.read_csv(df_destination) if df_destination.exists() else None
    current_df = pd.json_normalize(cleaned_pages_list)
    
    (
        pd
        .concat([existing_df, current_df]) # append to existing df
        .to_csv(df_destination, index = False)
    )
    