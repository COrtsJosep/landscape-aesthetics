import pickle
import pandas as pd
from pathlib import Path
import wikimedia_api_helpers

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns0_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns0.parquet'
download_log_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'temp' / 'downloaded_groups_log_ns0.pkl'

# This code executes the download of the images from the Wikimedia API. The download process
# is kept track through a list of downloaded groups, saved as a pickle file.

if download_log_path.exists():
    with open(download_log_path, 'rb') as f:
        downloaded_groups = pickle.load(f)
else:
    download_log_path.parent.mkdir(parents = True, exist_ok = True)
    downloaded_groups = []
    
df_ns0 = (
    pd
    .read_parquet(ns0_parquet_path, columns = ['title', 'country', 'query_id', 'thumbnail_source'])
    .dropna(subset = 'thumbnail_source')
    .loc[:, ['title', 'country', 'query_id']]
    .rename(columns = {'title': 'ns0_title'})
)

for group_name, group in df_ns0.groupby(by = ['country', 'query_id']):
    if group_name in downloaded_groups:
        continue
    else:
        group = group.reset_index(drop = True)
        group = wikimedia_api_helpers.add_ns6_title(group)
        batch_list = wikimedia_api_helpers.generate_batches(group)
        
        for batch in batch_list:
            wikimedia_api_helpers.download_batch(batch = batch, ns_type = 'ns0')
        
        downloaded_groups.append(group_name)
        with open(download_log_path, 'wb') as f:
            pickle.dump(downloaded_groups, f)

    break # please do not run the whole thing yet
