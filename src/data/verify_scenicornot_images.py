import pandas as pd
from PIL import Image
from tqdm import tqdm
from pathlib import Path

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
son_path = project_base_path / 'data' / 'external' / 'scenicornot'

def verify_image(image_path):
    # this function checks if a given path
    # contains a valid image
    if not image_path.is_file(): # first check if there is a file there
        return 'Not Transferred'

    try: # try to open it
        im = Image.open(image_path)
    except:
        return 'Unopenable'

    try: # verify its integrity
        im.verify()
    except:
        return 'Corrupted'

    im.close()
    try: # try to flip it. if truncated, this will give an error
        im = Image.open(image_path) 
        im.transpose(Image.FLIP_LEFT_RIGHT)
    except:
        return 'Truncated'

    im.close() 
    return 'OK' # everything looks good!

df_son = pd.read_csv(son_path / 'scenicornot.metadata.csv')
image_status = []
for filename in tqdm(df_son.loc[:, 'filename']): # check every filename. takes like 25 min
    image_status.append(
        verify_image(son_path / Path(filename))
    )

df_son.loc[:, 'image_status'] = image_status

print('Percentage of valid images: ', 100 * df_son.query('image_status == "OK"').shape[0] / df_son.shape[0], '%', sep = '')

destination_path = son_path / 'scenicornot.imagestatus.csv'
destination_path.parent.mkdir(parents = True, exist_ok = True)
df_son.loc[:, ['filename', 'image_status']].to_csv(destination_path, index = False)

# At a certain point we get the warning: "UserWarning: Corrupt EXIF data. 
# Expecting to read 2 bytes but only got 0."
#
# From the internet:
# it’s saying that it’s having trouble reading the image files. Based on some googling (look up “corrupt 
# EXIF data python error” and you’ll see a few discussions of this) it’s unlikely that the images are 
# actually corrupt, rather there’s a problem with how this particular Python library reads image files 
# that have EXIF metadata in the first place. The recommendation I see is to remove the EXIF data from 
# the image altogether
#
# Another guy:
# I’m not sure if it will ever affect the training. I was able to get rid of the warnings by using a 
# script to remove all exif data with the piexif library.