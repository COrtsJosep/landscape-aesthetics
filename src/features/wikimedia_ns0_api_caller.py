import tqdm
import pickle
import random
import pandas as pd
from pathlib import Path
import wikimedia_api_helpers

# we add randomness to the download order so that, in the unfortunate event
# that we had to suddenly stop the process, the sample that we would
# have would be as iid as possible
random.seed(42)

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns0_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns0.parquet'
download_log_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'temp' / 'downloaded_groups_log_ns0.pkl'

# This code executes the download of the images from the Wikimedia API. The download process
# is kept track through a list of downloaded groups, saved as a pickle file.

# First open the log of completed groups (just a list of the groups that have been
# downloaded so far. If it does not exist, create it.
def fetch_downloaded_groups(download_log_path):
    if download_log_path.exists():
        with open(download_log_path, 'rb') as f:
            downloaded_groups = pickle.load(f)
    else:
        download_log_path.parent.mkdir(parents = True, exist_ok = True)
        downloaded_groups = []
        
    return downloaded_groups

# Open the file of ns6 images. Drop duplicates based on whether they contain the same image.
df_ns0 = (
    pd
    .read_parquet(ns0_parquet_path, columns = ['title', 'country', 'query_id', 'thumbnail_source'])
    .dropna(subset = 'thumbnail_source')
    .loc[:, ['title', 'country', 'query_id']]
    .rename(columns = {'title': 'ns0_title'})
)

# We download by groups. A group is a country - query ID combination. A group has between 1 and 800 images
group_name_list = [group_name for group_name, _ in df_ns0.groupby(by = ['country', 'query_id'])]
random.shuffle(group_name_list) # a group name is for instance ('FR', 435), a country code and a query ID

for group_name, group in df_ns0.groupby(by = ['country', 'query_id']):
    if group_name in downloaded_groups:
        # Group has already been previously downloaded. Skip it then
        continue
    else:
        # Select the data corresponding to that group, split into batches of up to 50 images (that is the limit of the API)
        group = df_ns0.loc[(df_ns0.loc[:, 'country'] == group_name[0]) & (df_ns0.loc[:, 'query_id'] == group_name[1])].copy(deep = True)
        group = group.reset_index(drop = True)
        # Additionally: get the image that appears on the ns0 page - that is what we ultimately want to download
        group = wikimedia_api_helpers.add_ns6_title(group)
        batch_list = wikimedia_api_helpers.generate_batches(group)
        
        for batch in batch_list:
            # Download each batch
            wikimedia_api_helpers.download_batch(batch = batch, ns_type = 'ns0')

        # After successful download, add the name of the group to the list of downloaded
        # groups, and export that information.
        downloaded_groups = fetch_downloaded_groups(download_log_path) # update downloaded groups
        downloaded_groups.append(group_name) # add the one just downloaded
        with open(download_log_path, 'wb') as f:
            pickle.dump(downloaded_groups, f)