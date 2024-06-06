import requests
import pandas as pd
from pathlib import Path
import wikimedia_api_helpers

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns6.parquet'

df_ns6 = pd.read_parquet(ns6_parquet_path, columns = ['title', 'country', 'query_id'])

obs = df_ns6.sample(n = 50)
titles_lst = obs.loc[:, 'title'].tolist()
titles_str = '|'.join(titles_lst) # separate them with |s

headers = {'User-Agent': 'WikimediaCallerBot/1.0 (josep.cunqueroorts@uzh.ch)'}
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
    cleaned_pages_lst = []
    for page in pages_lst:
        title = page['title']
        query_id = df_ns6.loc[df_ns6.loc[:, 'title'] == page['title'], 'query_id'].item()
        country = df_ns6.loc[df_ns6.loc[:, 'title'] == page['title'], 'country'].item()
        
        metadata = {dct['name']: dct['value'] for dct in page['imageinfo'][0]['metadata']}
        
        page['imageinfo'][0]['extmetadata']
        for key in page['imageinfo'][0]['extmetadata'].keys():
            page[key] = page['imageinfo'][0]['extmetadata'][key]['value']
            # TODO: further parse results which are unpretty?

        page['url'] = page['imageinfo'][0]['url']
        page['mediatype'] = page['imageinfo'][0]['mediatype']
        page['explicit_content'] = 'yes' if 'badfile' in page['imageinfo'][0].keys() else None
        page['metadata_path'] = wikimedia_api_helpers.store_metadata(metadata = metadata,                                                                
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = title
        )
        page['image_path'] = wikimedia_api_helpers.download_image(url = page['url'], 
            country = country, 
            ns_type = 'ns6', 
            query_id = query_id, 
            title = title,
            headers = headers
        )
        del page['imageinfo']

        cleaned_pages_lst.append(page)       
        
    df = (
        pd
        .json_normalize(cleaned_pages_lst)
        #.drop(columns = ['ns', 'missing', 'known', 'CommonsMetadataExtension', 'Assessments']) # all empty or constant
    )
else:
    # try again, the batch is not complete, or see why
    ... 