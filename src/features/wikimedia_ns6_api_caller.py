import tqdm
import pickle
import random
import pandas as pd
from pathlib import Path
import wikimedia_api_helpers

# we add randomness to the download order so that, in the unfortunate event
# that we had to suddenly stop the process, the sample that we would
# have would be as iid as possible
valid_seed = False
while not valid_seed:
    try:
        seed = int(input('Please enter a seed value (an integer number): '))
        valid_seed = True
    except Exception as e:
        print(e)
        
random.seed(seed)

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_parquet_path = project_base_path / 'data' / 'processed' / 'wikimap_toolforge' / 'ns6.parquet'
download_log_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'temp' / 'downloaded_groups_log_ns6.pkl'

# This code executes the download of the images from the Wikimedia API. The download process
# is kept track through a list of downloaded groups, saved as a pickle file.

# First open the log of completed groups (just a list of the groups that have been
# downloaded so far. If it does not exist, create it.
def fetch_downloaded_groups(download_log_path):
    if download_log_path.exists():
        correctly_read = False
        while not correctly_read:
            try:
                with open(download_log_path, 'rb') as f:
                    downloaded_groups = pickle.load(f)
                correctly_read = True
            except:
                pass
        
    else:
        download_log_path.parent.mkdir(parents = True, exist_ok = True)
        downloaded_groups = []
        
    return downloaded_groups

def save_downloaded_groups(download_log_path, downloaded_groups):
    correctly_saved = False
    while not correctly_saved:
        try:
            with open(download_log_path, 'wb') as f:
                pickle.dump(downloaded_groups, f)
            correctly_saved = True
        except:
            pass

downloaded_groups = fetch_downloaded_groups(download_log_path)

# Open the file of ns6 images
df_ns6 = (
    pd
    .read_parquet(ns6_parquet_path, columns = ['title', 'country', 'query_id'])
    .rename(columns = {'title': 'ns6_title'})
)

# We download by groups. A group is a country - query ID combination. A group has between 1 and 800 images
group_name_list = [group_name for group_name, _ in df_ns6.groupby(by = ['country', 'query_id'])]
random.shuffle(group_name_list) # a group name is for instance ('FR', 435), a country code and a query ID

for group_name in tqdm.tqdm(group_name_list):
    if group_name in downloaded_groups:
        # Group has already been previously downloaded. Skip it then
        continue
    else:
        # Select the data corresponding to that group, split into batches of up to 50 images (that is the limit of the API)
        group = df_ns6.loc[(df_ns6.loc[:, 'country'] == group_name[0]) & (df_ns6.loc[:, 'query_id'] == group_name[1])].copy(deep = True)
        group = group.reset_index(drop = True)
        batch_list = wikimedia_api_helpers.generate_batches(group)
        
        for batch in batch_list:
            # Download each batch
            wikimedia_api_helpers.download_batch(batch = batch, ns_type = 'ns6')

        # After successful download, add the name of the group to the list of downloaded
        # groups, and export that information.
        downloaded_groups = fetch_downloaded_groups(download_log_path) # update downloaded groups
        downloaded_groups.append(group_name) # add the one just downloaded
        save_downloaded_groups(download_log_path, downloaded_groups)