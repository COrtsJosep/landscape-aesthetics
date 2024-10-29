import pandas as pd
import random
import os
import re

folder_path = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/'
output_folder = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/Image_Grid'
file_names = [f'merged_ns6_clean_{str(i).zfill(2)}.csv' for i in range(100)]

selected_images = []
total_required_images = 500  # 总共需要的图片数
lb = 6
ub = 7

# License info (patterns to match valid licenses, ignoring versions)
valid_licenses = ["^pd$", "^cc0$", "^cc-by(?:-\d+\.\d+)?$", "^cc-by-nc(?:-\d+\.\d+)?$"]

def is_valid_license(license):
    # Ensure license is a string
    if isinstance(license, str):
        # Check if the license matches any pattern in valid_licenses
        return any(re.match(pattern, license) for pattern in valid_licenses)
    return False

# Collect images from all CSV files without limiting to 5 per file
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)

    df = pd.read_csv(file_path)

    # Filter images based on predicted score and license
    filtered_df = df[(df['predicted_score'] >= lb) & 
                     (df['predicted_score'] < ub) &
                     (df['license'].apply(is_valid_license))]

    # Extend the selected images list with all qualifying images from this file
    selected_images.extend(filtered_df[['image_path', 'predicted_score', 'license', 'url']].values.tolist())

# If we have more images than required, randomly select the total_required_images count
if len(selected_images) > total_required_images:
    selected_images = random.sample(selected_images, total_required_images)

# Save the result in a new CSV file
output_filename = os.path.join(output_folder, f'selected_images_{lb}_to_{ub}.csv')
output_df = pd.DataFrame(selected_images, columns=['image_path', 'predicted_score', 'license', 'url'])
output_df.to_csv(output_filename, index=False)

print(f"Saved {len(selected_images)} images between {lb} and {ub} with valid licenses at {output_filename}.")
