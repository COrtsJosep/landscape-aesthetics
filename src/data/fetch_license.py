import pandas as pd
import os

input_folder_path = '/home/ubuntu/landscape-aesthetics/data/processed/wikimedia_commons/clean/'
output_folder_path = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_raw/' 

# make sure the output folder exists
os.makedirs(output_folder_path, exist_ok=True)

# go through every file
for i in range(100):
    # construct file name
    file_name = f'ns6_clean_{i:02d}.parquet'
    input_file_path = os.path.join(input_folder_path, file_name)
    
    # read parquet
    df = pd.read_parquet(input_file_path)
    
    # choose the columns
    selected_columns = df[['image_path', 'license', 'url', 'attribution']]
    
    # save as csv file
    output_file_name = f'ns6_clean_{i:02d}.csv'
    output_file_path = os.path.join(output_folder_path, output_file_name)
    selected_columns.to_csv(output_file_path, index=False)

    print(f"{output_file_name} has been saved to {output_folder_path}")
