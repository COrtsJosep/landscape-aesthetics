import tqdm
import math
import numpy as np
import pandas as pd
from pathlib import Path

pd.set_option('future.no_silent_downcasting', True)

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_wiki_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons').glob('ns6_*.parquet')
ns6_rot_paths = (project_base_path / 'data' / 'processed' / 'rotation_predicted').glob('ns6_rotation_*.parquet')

well_oriented_image_paths = ( # images predicted as being correctly oriented
    pd
    .concat([pd.read_parquet(ns6_rot_path) for ns6_rot_path in ns6_rot_paths])
    .query('rotation == 0')
    .loc[:, 'image_path']
)

relevant_cols = [ # columns where we cannot allow missing values
 'ns6_normalized_title',
 'ns6_unnormalized_title',
 'date_time',
 'gps_latitude',
 'gps_longitude',
 'gps_map_datum',
 'license',
 'url',
 'metadata_path',
 'image_path',
 'date_time_original',
 'query_id',
 'country']

def clean_df(path: Path, relevant_cols: list, well_oriented_image_paths: pd.Series) -> pd.DataFrame:
    """
    Takes a ns6 file and cleans the data, as well as filters out images that we do not want in
    the final version of the dataset.
    """
    df = pd.read_parquet(path).dropna(subset = relevant_cols)   
    logical_mask = (
    	(df.loc[:, 'image_path'].apply(lambda x: 'Not Downloaded' not in x))
    	& (df.loc[:, 'artist'].apply(lambda artist: not ('NASA' in artist or 'ESA' in artist) if type(artist) == str else True))
        & (df.loc[:, 'image_path'].isin(well_oriented_image_paths))
    )

    return (
        df
        .drop_duplicates(subset = 'image_path')
        .loc[logical_mask, 'image_path']
)

clean_image_paths = pd.Series(data = None, name = 'image_path')
for ns6_wiki_path in tqdm.tqdm(ns6_wiki_paths, total = 8, desc = 'Generating the filtered image path list'):
    clean_image_paths = pd.concat([clean_image_paths, clean_df(ns6_wiki_path, relevant_cols, well_oriented_image_paths)], ignore_index = True)

del well_oriented_image_paths
clean_image_paths = clean_image_paths.sample(frac = 1, random_state = 42).reset_index(drop = True) # shuffle the images
print('Number of clean, usable images:', clean_image_paths.shape[0])

def filter_df(path: Path, image_paths: pd.Series) - > pd.DataFrame:
    """
    Reads the data in the path, and keeps only the images that are in image_paths.
    """
    df = pd.read_parquet(path)
    return df.loc[df.loc[:, 'image_path'].isin(image_paths)]

chunk_size = 75000
num_chunks = math.ceil(clean_image_paths.shape[0] / chunk_size)
print(f'Going to split the database into {num_chunks} chunks of {chunk_size} observations!')
for i in tqdm.tqdm(range(num_chunks), desc = 'Creating and saving chunks'):
    chunk_image_paths = clean_image_paths[(i * chunk_size):((i + 1) * chunk_size)]
    ns6_wiki_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons').glob('ns6_*.parquet')
    output_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'clean' / f'ns6_clean_{i:02}.parquet'
    output_path.parent.mkdir(parents = True, exist_ok = True)

    (
        pd
        .concat([filter_df(ns6_wiki_path, chunk_image_paths) for ns6_wiki_path in ns6_wiki_paths])
        .drop_duplicates(subset = 'image_path')
        .to_parquet(output_path, index = False)
    )
    
        
