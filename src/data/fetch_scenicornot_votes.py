import pandas as pd
import urllib.request
from pathlib import Path

# Data comes from http://scenicornot.datasciencelab.co.uk/. Check out
# the page http://scenicornot.datasciencelab.co.uk/faq.
file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
resource_destination = project_base_path / 'data' / 'external' / 'scenicornot' / 'votes.tsv'
resource_url = 'http://scenicornot.datasciencelab.co.uk/votes.tsv'

# fetch the zip file
print('Retrieving the TSV file...')
urllib.request.urlretrieve(resource_url, resource_destination)

# add extra column with (probably) the gridimage_id,
# the equivalent at scenicornot.metadata.csv
print('Adding Grid ID column...')
(
    pd
    .read_csv(resource_destination, sep = '\t')
    .assign(gridimage_id = lambda df: df.loc[:, 'Geograph URI'].apply(lambda uri: uri.split('/')[-1]))
    .to_csv(resource_destination, sep = '\t', index = False)
)


print('All done!')