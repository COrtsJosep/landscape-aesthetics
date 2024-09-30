import pandas as pd
from PIL import Image
from pathlib import Path

file_location_path = Path.cwd()
project_base_path = file_location_path.parent.parent
ns6_parquet_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'ns6_1.parquet'
labelled_csv_path = project_base_path / 'data' / 'processed' / 'landscape_handmade' / 'landscapes_test.csv'

# This programs shows the user images from wikimedia, and the user labels them as landscapes or as
# non-landscapes.

labelled_csv_path.parent.mkdir(parents = True, exist_ok = True) # create directory for output
df = ( # load df of images downloaded so far
    pd
    .read_parquet(ns6_parquet_path, columns = ['image_path']) # only path needed
    .query('image_path != "Not Downloaded - Download Error"') # drop download errors
    .query('image_path != "Not Downloaded - Transformation Error"')
    .query('image_path != "Not Downloaded - Saving Error"')
)

name = input('Please enter your name: ') # enter name

proceed = True
while proceed:
    df_labelled = ( # load the csv of labelled data
        pd.read_csv(labelled_csv_path) 
        if labelled_csv_path.exists() # ...but only if it already exists
        else pd.DataFrame(columns = ['image_path', 'landscape', 'labeller']) # otherwise create an empty df
    )
    df_subset = ( # create a batch
        df
        .loc[~df.loc[:, 'image_path'].isin(df_labelled.loc[:, 'image_path'])] # filter out already labelled images
        .sample(n = 25) # take a batch of 25
        .reset_index(drop = True) # index them 
        .copy()
    )
    
    n = len(df_subset) # will always be 25... until all data has been labelled ;)
    i = 0
    while i < n: # while not all images are labelled
        # show image and image name
        display(Image.open('/home/ubuntu/landscape-aesthetics/' + df_subset.loc[i, 'image_path']))
        print(f'({i+1}/{n}) Showing:', df_subset.loc[i, 'image_path'])

        # record answer
        valid_answer = False
        if i == 0:
            while not valid_answer:
                answer = input('Is this a landscape, yes (y) or no (n)? ')
                valid_answer =  answer in ('y', 'n')
        else:
            while not valid_answer:
                answer = input('Is this a landscape, yes (y) or no (n)? Alternatively, type (p) to go back to the previous image. ') 
                valid_answer = answer in ('y', 'n', 'p')

        # act accordingly
        if answer == 'p':
            i -= 1
        elif answer == 'y':
            df_subset.loc[i, 'landscape'] = 1
            i += 1
        else:
            df_subset.loc[i, 'landscape'] = 0
            i += 1

    ( # export the results
        pd
        .concat([df_labelled, df_subset.assign(labeller = name)])
        .to_csv(labelled_csv_path, index = False)
    )

    # decide if you want to go for another round
    valid_decision = False
    while not valid_decision:
        decision = input(f'Batch of {n} complete - do you want to do another one, yes (y) or no (n)? ')
        valid_decision = decision in ('y', 'n')

    proceed = (decision == 'y')