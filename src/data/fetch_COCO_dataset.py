import zipfile
import pandas as pd
import urllib.request
from pathlib import Path

# Data comes from https://cocodataset.org/#home
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

train_resource_destination = project_base_path / 'data' / 'external' / 'COCO' / 'train2014.zip'
train_resource_url = 'http://images.cocodataset.org/zips/train2014.zip'
val_resource_destination = project_base_path / 'data' / 'external' / 'COCO' / 'val2014.zip'
val_resource_url = 'http://images.cocodataset.org/zips/val2014.zip'

# fetch the zip file
print('Retrieving the ZIP file...')
urllib.request.urlretrieve(train_resource_url, train_resource_destination)
urllib.request.urlretrieve(val_resource_url, val_resource_destination)

# extract the desired shape file
print('Extracting the ZIP file...')
with zipfile.ZipFile(train_resource_destination, 'r') as zip_ref:
    zip_ref.extractall(path = train_resource_destination.parent)
with zipfile.ZipFile(val_resource_destination, 'r') as zip_ref:
    zip_ref.extractall(path = val_resource_destination.parent)

# rename it and delete the zip file
print('Deleting the ZIP file...')
train_resource_destination.unlink()
val_resource_destination.unlink()

print('All done!')