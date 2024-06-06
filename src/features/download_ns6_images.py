import requests
import pandas as pd
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns6.parquet'

df_ns6 = pd.read_parquet(ns6_parquet_path).iloc[:, 1:] 
#display(df_ns6.head())

obs = df_ns6.sample(n = 25)
titles_lst = obs.loc[:, 'title'].tolist()
titles_str = '|'.join(titles_lst) # separate them with |s

headers = {
    # https://api.wikimedia.org/wiki/Authentication#Personal_API_tokens
        'User-Agent': 'Wikimedia Caller - please do not block us - send us a message!' ,
        'From': 'josep.cunqueroorts@uzh.ch'
    }

api_query = f'https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|mediatype|metadata|extmetadata|badfile&titles={titles_str}&format=json'
r = requests.get(api_query, headers = headers)
r_json = r.json()

if 'batchcomplete' in r_json.keys():
    print(r_json['batchcomplete'])
    
    if 'normalized' in r_json['query']:
        # some file titles had to be normalized. see why or just record the title change
        ...    
    pages_dct = r_json['query']['pages']
    pages_lst = [pages_dct[key] for key in pages_dct.keys()]
    cleaned_pages_lst
    for page in pages_lst:
        ### metadata part. save it somewhere else?
        metadata = [{dct['name']: dct['value']} for dct in page['imageinfo'][0]['metadata']]
        
        ### extmetadata part. 
        page['imageinfo'][0]['extmetadata']
        for key in page['imageinfo'][0]['extmetadata'].keys():
            page[key] = page['imageinfo'][0]['extmetadata'][key]['value']
            # further parse results which are unpretty?

        page['url'] = page['imageinfo'][0]['url']
        page['mediatype'] = page['imageinfo'][0]['mediatype']
        page['explicit_content'] = 'yes' if 'badfile' in page['imageinfo'][0].keys() else None
        page['metadata_path'] = ...
        page['image_path'] = ...
        del page['imageinfo']

        cleaned_pages_lst.append(page)

        ### download image
        
        
    df = (
        pd
        .json_normalize(cleaned_pages_lst)
        #.drop(columns = ['ns', 'missing', 'known', 'CommonsMetadataExtension', 'Assessments']) # all empty or constant
    )
else:
    # try again, the batch is not complete, or see why
    ... 