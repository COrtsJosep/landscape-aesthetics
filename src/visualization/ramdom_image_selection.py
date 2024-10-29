import pandas as pd
import random
import os


folder_path = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/' 
output_folder = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/Image_Grid'
file_names = [f'merged_ns6_clean_{str(i).zfill(2)}.csv' for i in range(100)]

selected_images = []
num_per_file = 5
lb = 6
ub = 7

# license info
valid_licenses = ["pd", "cc0", "cc-by", "cc-by-sa"]

def is_valid_license(license):
    if isinstance(license, str):  # ensure license is a string
        return any(license.startswith(valid_license) for valid_license in valid_licenses)
    return False

# go through every csv file
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    
    df = pd.read_csv(file_path)
    
    # select images that are predicted between lower bound and upper bound 
    # filtered_df = df[(df['predicted_score'] >= lb) & (df['predicted_score'] < ub)]

    # add one standard to filter out the license
    filtered_df = df[(df['predicted_score'] >= lb) & 
                 (df['predicted_score'] < ub) & 
                 (df['license'].apply(is_valid_license))]
    
    if len(filtered_df) < num_per_file:
        print(f"Error：File {file_name} contains less than {num_per_file} images within the interval")
    else:
        # randomly select 5 images
        selected_rows = filtered_df.sample(n=num_per_file)
        
        # save the path and score
        selected_images.extend(selected_rows[['image_path', 'predicted_score', 'license', 'url']].values.tolist())
    

# save the result in a new csv file
output_filename = os.path.join(output_folder, f'selected_images_{lb}_to_{ub}.csv')
output_df = pd.DataFrame(selected_images, columns=['image_path', 'predicted_score', 'license', 'url'])
output_df.to_csv(output_filename, index=False)

print(f"Saved {len(selected_images)} images between {lb} and {ub} with valid licenses at {output_filename}.")