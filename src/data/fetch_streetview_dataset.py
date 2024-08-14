import zipfile
import pandas as pd
import urllib.request
from pathlib import Path

# Data comes from https://www.kaggle.com/datasets/paulchambaz/google-street-view,
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'streetview.zip'
resource_url_file = project_base_path / 'streetview_url.txt'

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

print('Moving all images up a level...')
for path in (resource_destination.with_suffix('') / 'dataset').iterdir():
    new_path = Path(str(path).replace('dataset/', ''))
    path.replace(new_path)

(resource_destination.with_suffix('') / 'dataset').rmdir()

print('All done!')