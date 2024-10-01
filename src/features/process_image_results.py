import numpy as np
import inflection
import pandas as pd
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
wikimedia_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons'

cols_stringify = [#'ns',
 #'missing',
 #'known',
 #'imagerepository',
 #'ns6_normalized_title',
 #'ns6_unnormalized_title',
 #'date_time',
 #'object_name',
 #'commons_metadata_extension',
 #'categories',
 #'assessments',
 #'gps_latitude',
 #'gps_longitude',
 #'gps_map_datum',
 'image_description',
 'date_time_original',
 #'credit',
 #'artist',
 #'license_short_name',
 #'usage_terms',
 #'attribution_required',
 #'copyrighted',
 #'restrictions',
 #'license',
 #'url',
 #'image_width',
 #'image_height',
 #'mediatype',
 #'explicit_content',
 #'metadata_path',
 #'image_path',
 #'query_id',
 #'country',
 #'permission',
 'attribution',
 #'license_url',
 #'pageid',
 #'author_count'
]

def process_df(df_path: Path) -> pd.DataFrame:
    '''
    Given a path to a csv, reads it as a df, adds identifier columns,
    renames columns, drops duplicates, and returns the result.
    '''
    if 'images_from_uk.csv' in str(df_path):
        return pd.DataFrame()
        
    df = pd.read_csv(df_path)

    df.loc[:, 'query_id'] = df_path.name.split('_')[1][2:]
    df.loc[:, 'country'] = df_path.name.split('_')[0]
    
    df.columns = [inflection.underscore(colname) for colname in df.columns]
    df.drop_duplicates(subset = 'ns6_unnormalized_title') # no duplicates (title is the unique identifier)

    return df

def get_row_number(dfs):
    rows = 0
    for df in dfs:
        rows += df.shape[0]

    return rows

def save_dfs(dfs, ns_type, saved_times, cols_stringify):
    output_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / f'{ns_type}_{saved_times}.parquet'
    output_path.parent.mkdir(parents = True, exist_ok = True)
    
    df = (
        pd
        .concat(dfs)
        .drop_duplicates(subset = 'ns6_unnormalized_title') # again drop duplicates, for close-border cases
        .query('ns == 6')
        .reset_index()
        .drop(labels = ['index', 'uk_or_not'], axis = 1, errors = 'ignore') # ignore if these columns are not in the df
    )
    df.loc[:, cols_stringify] = df.loc[:, cols_stringify].astype(str, errors = 'ignore').replace('nan', np.nan)
    
    df.to_parquet(output_path, index = False)

ns_foldernames = []
for country_path in (wikimedia_path / 'dataframes').glob('*'):
    ns_foldernames += [path.name for path in country_path.glob('*')]
ns_types = set(ns_foldernames)

for ns_type in ns_types:
    dfs = []
    saved_times, saved_rows = 0, 0
    print('\nNS type:', ns_type)
    for country_path in (wikimedia_path / 'dataframes').glob('*'):
        print('Just begun with', country_path.name)
        dfs += [process_df(df_path) for df_path in (country_path / ns_type).glob('*.csv')]

        if get_row_number(dfs) > 1000000:
            save_dfs(dfs, ns_type, saved_times, cols_stringify)
            saved_times += 1
            saved_rows += get_row_number(dfs)
            
            dfs = []
            
            print('Saved one chunk!')

    if 0 < get_row_number(dfs) <= 1000000:
        save_dfs(dfs, ns_type, saved_times, cols_stringify)
        saved_times += 1
        saved_rows += get_row_number(dfs)
        
    print(f'{saved_rows} {ns_type} images have already been processed') 