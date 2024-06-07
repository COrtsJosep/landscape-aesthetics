import json
import time
import requests
import urllib.parse
import pandas as pd
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
headers = {'User-Agent': 'WikimediaCallerBot/1.0 (josep.cunqueroorts@uzh.ch)'}

def call_api(query_string, rest_time, task):
    time.sleep(rest_time)
    
    responded = False
    times_slept = 0
    while not responded or response.status_code != 200:
        try:
            response = requests.get(query_string, headers = headers, timeout = 60)
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

def transform_image(image_path):
    # transform the image, as in: rescale, crop, convert to grayscale, convert to jpeg... to be decided
    ...
    new_image_path = image_path
    return new_image_path

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
    resource_destination.parent.mkdir(parents = True, exist_ok = True)

    response = call_api(query_string = url, rest_time = 0, task = 'fetch image')
    with open(resource_destination, 'wb') as f:
        f.write(response.content)
    resource_location = transform_image(resource_destination)
    return str(resource_location.relative_to(project_base_path))

def download_batch(batch, ns_type):
    titles_lst = [urllib.parse.quote(title) for title in batch.loc[:, 'title'].tolist()] # in case of weird characters
    titles_str = '|'.join(titles_lst) # separate them with |s
    
    api_query = f'https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|mediatype|metadata|extmetadata|badfile&titles={titles_str}&format=json'

    batch_complete = False
    while not batch_complete:
        response = call_api(query_string = api_query, 
                            rest_time = 1,
                            task = 'fetch image data')
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
    pages_lst = [pages_dct[key] for key in pages_dct.keys()]
    cleaned_pages_lst = []
    
    for page in pages_lst: # write documentation
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

        cleaned_pages_lst.append(page)       
    
    df_destination = (
        project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'dataframes' 
        / country / ns_type / f'{country}_id{query_id}_{ns_type}.csv' 
    )
    df_destination.parent.mkdir(parents = True, exist_ok = True)
    
    existing_df = pd.read_csv(df_destination) if df_destination.exists() else None
    current_df = pd.json_normalize(cleaned_pages_lst)
    
    (
        pd
        .concat([existing_df, current_df]) # append to existing df
        .to_csv(df_destination, index = False)
    )
    