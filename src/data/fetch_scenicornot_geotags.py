import gzip
import shutil
import urllib.request
from pathlib import Path

# Define where this file is, and relative to it, the project directory,
# and where the zip file should be placed.
# Data comes from http://data.geograph.org.uk/dumps/
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'scenicornot' / 'gridimage_base.tsv.gz'
resource_url = 'http://data.geograph.org.uk/dumps/gridimage_base.tsv.gz'

# fetch the zip file
print('Retrieving the ZIP file...')
urllib.request.urlretrieve(resource_url, resource_destination)

# extract the desired shape file
print('Extracting the ZIP file...')
with gzip.open(resource_destination, 'rb') as f_in:
    with open(resource_destination.with_suffix(''), 'w') as f_out:
        f_out.write(f_in.read().decode('latin'))

# rename it and delete the zip file
print('Deleting the ZIP file...')
resource_destination.unlink()

print('All done!')

# I asked the people from Geograph why the SoN metadata does not include the geolocation, and where could we find it.
# This is their answer:

# You can get the data from: https://data.geograph.org.uk/dumps/
# Either TSV (tab separated) or mysqldump format. The 'gridimage_base' has the lat/long (and the grid-square reference)
# OR the 'gridimage_geo' has eastings/northings (OSGB)
# ... one warning scenic or not, originally tried to pick one image per square. Will find that some images have moved 
# since then, so the coverage is not perfect, there are some squares that will appear to have multiple images.
# Also dont remember the details, but I think there was an issue with data processing in their data (when they 
# converted our eastings/northing to lat long) - which does mean sometimes the locations was slightly off.
# The above files (from our dumps folder) should have the latest position, and confident the OSGB - WGS84 transformation
# is reliable now (to within about 6m anyway!) 