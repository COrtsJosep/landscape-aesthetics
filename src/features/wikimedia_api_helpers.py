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
token_file = project_base_path / 'wikimedia_auth.txt'

with open(token_file, 'r') as f:
    wikidata_token = f.read()
    
wikimedia_headers = {'User-Agent': 'WikimediaCallerBot/1.0 (josep.cunqueroorts@uzh.ch)'}
wikidata_headers = {'User-Agent': 'WikidataCallerBot/1.0 (josep.cunqueroorts@uzh.ch)',
                    'Authorization': f'{wikidata_token}'}

def get_image_title(ns0_title: str) -> tuple:
    '''
    Given a ns6 title, calls the Wikidata API to fetch the images (only the first is taken)
    from the Wikidata page of the object. Also fetches the coordinates. In case there
    are many coordinate pairs (think, for instance, a street that has the coordinates of the
    beginning and of the end), it takes the first ones only.
    '''    
    url = f'https://www.wikidata.org/w/rest.php/wikibase/v0/entities/items/{ns0_title}'
    
    response = call_api(url = url, rest_time = 0, task = 'fetch images in ns0 page', headers = wikidata_headers)
    stats = response.json()['statements']
    first_image = ['File:' + stats['P18'][0]['value']['content'] if 'P18' in stats.keys() else None]
    
    if 'P625' in stats.keys():
        content = stats['P625'][0]['value']['content'] # we select only the first coordinate pair
        first_coords = [content['latitude'], content['longitude'], content['precision']]
    else: 
        first_coords = [None] * 3
    
    return first_image + first_coords

def add_ns6_title(group: pd.DataFrame) -> pd.DataFrame:
    '''
    Gets a group, creates a series with the corresponding names of the 
    images found in the Wikidata pages of the respective objects, and
    appends that list to the group, which is then returned.
    '''
    ns6_title_series = ( # create a series with the ns6 data
            group
            .loc[:, 'ns0_title']
            .apply(lambda title: get_image_title(title))
        )
    group = (
        group # merge it with the original dataframe, by the index
        .join(pd.DataFrame(ns6_title_series.tolist(), 
                           index = ns6_title_series.index, 
                           columns = ['ns6_title', 'ns0_lat', 'ns0_lon', 'ns0_precision'])
             )
    )

    return group
                    
def acceptable_batch_list(batch_list: list) -> bool:
    '''
    Given a list of dataframes, check if it is an acceptable partition. The reasoning
    being that if the batch is too big, then the request sent to the Wikidata API is too
    big, and the endpoint refuses to respond. This happens if the length of the URI that
    we send is approx. larger than 8200 characters long. Approx. 150 characters are 
    headers, endpoint URI, other parameters. The bulk is the concatenation of the titles
    in the batch. 
    This function tests if for every batch, the concatenation of the image names (converted
    to URL-accepted characters) is shorter than 8000 characters long. If it holds for all batches,
    then True is returned, else False.
    '''
    titles_strings_list = [urllib.parse.quote('|'.join(batch.loc[:, 'ns6_title'])) for batch in batch_list]
    size_list = [len(titles_string) for titles_string in titles_strings_list]
    
    return all([size < 8000 for size in size_list])

def generate_batches(group: pd.DataFrame) -> list:
    '''
    Given a dataframe, a list of equaly-sized batches (except for the last batch, which is 
    usually smaller) is returned.
    The function first splits the dataframe in batches of 50, but if the batches are too large
    to be sent to the API, the split is done again, but with batch size 45. If not, again, with
    batch size 40, etc, etc. Batches larger than 50 titles are not allowed by the API.
    '''
    batch_size = 50
    num_batches = math.ceil(group.shape[0] / batch_size) # in groups of batch_size
    batch_list = [group.loc[(batch_size*i):(batch_size*(i + 1) - 1)] for i in range(num_batches)]
    
    while not acceptable_batch_list(batch_list) and batch_size != 1:
        batch_size = max(batch_size - 5, 1) # minimum batch size is 1
        num_batches = math.ceil(group.shape[0] / batch_size) # in groups of batch_size
        batch_list = [group.loc[(batch_size*i):(batch_size*(i + 1) - 1)] for i in range(num_batches)]

    return batch_list

def call_api(url: str, rest_time: int, task: str, params: dict = None, headers: dict = None) -> requests.models.Response:
    '''
    Generic function to call an API, given some parameters, handle typical unsuccessful trials, and 
    return the response. Two unsuccessful cases are handled:
    - Endpoint does not answer and the response timeout expires. Other errors are also "elegantly" caught.
    - Endpoint returns a non-200 HTTP code. 
    In both cases, the request is sent again after a short pause. After 5 failed calls, the process is 
    paused until there is human input.
    '''
    time.sleep(rest_time)
    
    responded = False
    times_slept = 0
    while not responded or response.status_code != 200:
        try:
            response = requests.get(url, params = params, headers = headers, timeout = 60)
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

def center_crop(image: Image) -> Image:
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


def transform_image(image: Image) -> Image:
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

def download_image(url: str, country: str, ns_type: str, query_id: int, title: str) -> str:
    '''
    Downloads an image at a path determined by the attributes of the image. Returns the 
    download path.
    '''
    print(url)
    resource_destination = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'images' / country / ns_type / str(query_id) / title
    resource_destination = resource_destination.with_suffix('.jpeg') # whatever it is, it will be converted to jpeg
    resource_destination.parent.mkdir(parents = True, exist_ok = True)

    response = call_api(url = url, rest_time = 0, task = 'fetch image', headers = wikimedia_headers) # fetch image
    image = Image.open(io.BytesIO(response.content)) # read it-in memory - do not save it yet
    image = transform_image(image) # transform it
    image.save(resource_destination) # now save it

    return str(resource_destination.relative_to(project_base_path))

def download_batch(batch: pd.DataFrame, ns_type: str) -> None:
    '''
    Most important function of the file.
    Takes a batch and calls the Wikidata API about the available
    information regarding the images in the batch. The response contains
    many useful information, including the image download URL. However for
    our purposes, we need to clean the information given by the API.
    For each image, we download it, and we also download the metadata. The meta-
    data contains information about the camera, and shot parameters, which are 
    device-dependent - this is why we store it away as a json, instead of trying
    to agreggate all metadata loads into a table.
    The common fields of the images (coordinates, title, capture date...) are
    stored in a dataframe and then saved as a csv.
    '''
    
    titles_str = '|'.join(batch.loc[:, 'ns6_title']) # join the titles, separated with |s
    
    api_endpoint = 'https://en.wikipedia.org/w/api.php'
    params = { # set up query load as a dictionary
        'action': 'query',
        'prop': 'imageinfo',
        'iiprop': 'url|mediatype|metadata|extmetadata|badfile',
        'titles': titles_str,
        'format': 'json'
    }

    batch_complete = False
    while not batch_complete: # the API returns a field called "batchcomplete" if all info requested was delivered
        response = call_api(url = api_endpoint,
                            rest_time = 1,
                            task = 'fetch image data',
                            params = params,
                            headers = wikimedia_headers)
        response_json = response.json()
        batch_complete = ('batchcomplete' in response_json.keys())

    # some image names are normalized. this does not always happen.
    # it is due to weird characters. to keep track, we create a dictionary
    # of new name - old name
    renaming_dict = {title: title for title in batch.loc[:, 'ns6_title']}
    if 'normalized' in response_json['query'].keys():
        for element in response_json['query']['normalized']:
            renaming_dict[element['to']] = element['from']
        # some file titles might have been normalized. to see which, uncomment:
        #print('Titles were normalized. See:', response_json['query']['normalized'])
            
    pages_dct = response_json['query']['pages'] # extract the response
    pages_list = [pages_dct[key] for key in pages_dct.keys()]
    cleaned_pages_list = []

    for page in pages_list:
        # This is the main loop, which iterates over every returned item. the item "page" is
        # cleaned and at the end appended at the cleaned_pages_list.
        # "page" is a dictionary
        ns6_normalized_title = page['title'] # title returned by the API
        ns6_unnormalized_title = renaming_dict[ns6_normalized_title] # original title in our records (often the same)
        page['ns6_normalized_title'] = ns6_normalized_title
        page['ns6_unnormalized_title'] = ns6_unnormalized_title

        obs_record = batch.loc[batch.loc[:, 'ns6_title'] == ns6_unnormalized_title]
        query_id = obs_record.loc[:, 'query_id'].item() # search back which is the query_id
        country = obs_record.loc[:, 'country'].item() # and country of the image

        metadata = {dct['name']: dct['value'] for dct in page['imageinfo'][0]['metadata']} # find the metadata and turn it into dict
        
        page['imageinfo'][0]['extmetadata'] # extmetadata has some common fields which are useful for us
        for key in page['imageinfo'][0]['extmetadata'].keys(): # but the format needs to be modified a bit
            page[key] = page['imageinfo'][0]['extmetadata'][key]['value']
            # TODO: further parse results which are unpretty?

        # set "by hand" some attributes
        page['ns'] = ns_type[2] # take the number from the string ns0 or ns6
        page['url'] = page['imageinfo'][0]['url']
        page['mediatype'] = page['imageinfo'][0]['mediatype']
        page['explicit_content'] = 'yes' if 'badfile' in page['imageinfo'][0].keys() else None
        page['metadata_path'] = store_metadata(metadata = metadata, # store the metadata
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = ns6_unnormalized_title
        )
        page['image_path'] = download_image(url = page['url'], # download the image
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = ns6_unnormalized_title
        )

        if ns_type == 'ns0': # in case of ns0, also add the fields specific to ns0 observations
            page['ns0_title'], page['ns0_lat'], page['ns0_lon'], page['ns0_precision'] = obs_record[['ns0_title', 'ns0_lat', 'ns0_lon', 'ns0_precision']]
        
        del page['title'] # delete unnecessary fields (we already have the data
        del page['imageinfo'] # spread in other fields

        cleaned_pages_list.append(page) # add the cleaned result
    
    df_destination = ( # define path to export csv
        project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'dataframes' 
        / country / ns_type / f'{country}_id{query_id}_{ns_type}.csv' 
    )
    df_destination.parent.mkdir(parents = True, exist_ok = True)
    
    existing_df = pd.read_csv(df_destination) if df_destination.exists() else None
    current_df = pd.json_normalize(cleaned_pages_list)
    
    ( # here we concatenate the csv with all existing records of previous batches
        pd
        .concat([existing_df, current_df]) # append to existing df
        .to_csv(df_destination, index = False)
    )
    