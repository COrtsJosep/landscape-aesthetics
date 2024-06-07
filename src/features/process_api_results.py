import pandas as pd
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
wikimap_path = project_base_path / 'data' / 'interim' / 'wikimap_toolforge'

rename_dict = {
    'coordinates.lat': 'resource_lat',
    'coordinates.lon': 'resource_lon',
    'coordinates.primary': 'resource_primary_coords',
    'coordinates.bearing': 'resource_bearing'
}

def process_df(df_path):
    df = pd.read_csv(df_path)

    df = df.rename(columns = rename_dict) # rename accoding to convention
    df.columns = [x.replace('.', '_') for x in df.columns.to_list()] # no dots in the column names
    df = df.loc[~df.loc[:, 'resource_lat'].isna()] # drop if coordinates are empty
    df = df.drop_duplicates(subset = 'title') # no duplicates (title is the unique identifier)
    df = df.loc[~df.loc[:, 'title'].apply(lambda title: 'view of earth' in title.lower())] # we do not want pictures from space

    return df

ns_foldernames = []
for country_path in wikimap_path.glob('*'):
    ns_foldernames += [path.name for path in country_path.glob('*')]
ns_types = set(ns_foldernames)

for ns_type in ns_types:
    dfs = []
    print('\nNS type:', ns_type)
    for country_path in wikimap_path.glob('*'):
        print('Just begun with', country_path.name)
        dfs += [process_df(df_path) for df_path in (country_path / ns_type).glob('*.csv')]
    
    output_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / f'{ns_type}.parquet'
    output_path.parent.mkdir(parents = True, exist_ok = True)
    
    (
        pd
        .concat(dfs)
        .drop_duplicates(subset = 'title') # again drop duplicates, for close-border cases
        .reset_index()
        .to_parquet(output_path, index = False)
    )

