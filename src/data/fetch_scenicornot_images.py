import zipfile
import urllib.request
from pathlib import Path
import os

# Define where this file is, and relative to it, the project directory,
# and where the zip file should be placed
# Data comes from http://scenicornot.datasciencelab.co.uk/, got asked by creating
# a ticket at https://company.geograph.org.uk/support/
file_location_path = Path(os.getcwd())
project_base_path = file_location_path.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'scenicornot.zip'
resource_url = 'https://s3.eu-west-1.amazonaws.com/data.geograph.org.uk/datasets/scenicornot.zip'

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

print('All done!')