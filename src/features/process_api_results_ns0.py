import ast
import numpy as np
import pandas as pd
from pathlib import Path

# IN PROGRESS

#pd.set_option('display.max_columns', None)

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
wikimap_path = project_base_path / 'data' / 'interim' / 'wikimap_toolforge'

def process_ns0_df(df_path):
    df = pd.read_csv(df_path)
    
    df.loc[:, 'resource_lat'] = df.loc[:, 'coordinates'].apply(lambda x: ast.literal_eval(x)[0]['lat']) # maybe improve
    df.loc[:, 'resource_lon'] = df.loc[:, 'coordinates'].apply(lambda x: ast.literal_eval(x)[0]['lon'])
    df.loc[:, 'are_primary_coords'] = df.loc[:, 'coordinates'].apply(lambda x: ast.literal_eval(x)[0]['primary'])
    df.loc[:, 'count_labels'] = df.loc[:, 'entityterms.label'].apply(lambda x: len(ast.literal_eval(x)) if type(x) == str else 0)
    df.loc[:, 'labels'] = df.loc[:, 'entityterms.label'].apply(lambda x: ','.join(ast.literal_eval(x)) if type(x) == str else np.nan)
    
    df = df.drop(columns = ['entityterms.label', 'coordinates'])
    df.columns = [x.replace('.', '_') for x in df.columns.to_list()]
    df = df.loc[~df.loc[:, 'resource_lat'].isna()] # drop if coordinates are empty

    return df

ns0_dfs = []
for country_path in wikimap_path.glob('*'):
    ns0_dfs += [process_ns0_df(df_path) for df_path in (country_path / 'ns0').glob('*.csv')]

output_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns0.parquet'
output_path.parent.mkdir(parents = True, exist_ok = True)

(
    pd
    .concat(ns0_dfs)
    .drop_duplicates(subset = ['pageid', 'title'])
    .reset_index()
    .to_parquet(output_path, index = False)
)