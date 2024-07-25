import zipfile
import pandas as pd
import urllib.request
from pathlib import Path

# Define where this file is, and relative to it, the project directory,
# and where the zip file should be placed
# Data comes from https://www.kaggle.com/datasets/birdy654/scene-classification-images-and-audio?resource=download,
# we must cite them if we use their data.
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'sceneclassification.zip'
resource_url_file = project_base_path / 'scene_classification_url.txt'

with open(resource_url_file, 'r') as f:
    resource_url = f.read()

# fetch the zip file
print('Retrieving the ZIP file...')
urllib.request.urlretrieve(resource_url, resource_destination)

# extract the desired shape file
print('Extracting the ZIP file...')
with zipfile.ZipFile(resource_destination, 'r') as zip_ref:
    zip_ref.extractall(path = resource_destination.with_suffix(''))

# rename it and delete the zip file
print('Deleting the ZIP file...')
resource_destination.unlink()

# keep only relevant information
print('Deleting irrelevant data...')
(
    pd
    .read_csv(resource_destination.with_suffix('') / 'dataset.csv')
    .assign(outdoors = lambda df: df.loc[:, 'CLASS1'].apply(lambda cls: 1 if cls == 'OUTDOORS' else 0))
    .loc[:, ['IMAGE', 'outdoors']]
    .rename(columns = {'IMAGE': 'image_path'})
    .to_csv(resource_destination.with_suffix('') / 'dataset.csv', index = False)
)

print('All done!')