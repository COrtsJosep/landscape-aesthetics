import zipfile
import urllib.request
from pathlib import Path

# Define where this file is, and relative to it, the project directory,
# and where the zip file should be placed
# Data comes from https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'geoshapes' / 'country_geoshapes.shp.zip'
resource_url = 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_01M_2021_4326.shp.zip'

# fetch the zip file
print('Retrieving the ZIP file...')
urllib.request.urlretrieve(resource_url, resource_destination)

# extract the desired shape file
print('Extracting the ZIP file...')
with zipfile.ZipFile(resource_destination, 'r') as zip_ref:
    zip_ref.extractall(path = resource_destination.parent)

# rename it and delete the zip file
print('Renaming and deleting...')
resource_destination.unlink()
for filepath in resource_destination.parent.glob('*'):
    suffix = filepath.suffix
    filepath.rename(filepath.parent / ('country_geoshapes' + suffix))
#(resource_destination.parent / 'NUTS_RG_01M_2021_4326.shp').rename(resource_destination.parent / 'country_geoshapes.shp')
#(resource_destination.parent / 'NUTS_RG_01M_2021_4326.shx').rename(resource_destination.parent / 'country_geoshapes.shx')


print('All done!')