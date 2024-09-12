import inflection
import pandas as pd
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
wikimedia_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons'

def process_df(df_path: Path) -> pd.DataFrame:
    '''
    Given a path to a csv, reads it as a df, adds identifier columns,
    renames columns, drops duplicates, and returns the result.
    '''
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

def save_dfs(dfs, ns_type, saved_times):
    output_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / f'{ns_type}_{saved_times}.parquet'
    output_path.parent.mkdir(parents = True, exist_ok = True)
    
    df = (
        pd
        .concat(dfs)
        .drop_duplicates(subset = 'ns6_unnormalized_title') # again drop duplicates, for close-border cases
        .reset_index()
        .astype(str)
    )
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
            save_dfs(dfs, ns_type, saved_times)
            saved_times += 1
            saved_rows += get_row_number(dfs)
            
            dfs = []
            
            print('Saved one chunk!')

    if get_row_number(dfs) <= 1000000:
        save_dfs(dfs, ns_type, saved_times)
        saved_times += 1
        saved_rows += get_row_number(dfs)
        
    print(f'{saved_rows} {ns_type} images have already been processed') 