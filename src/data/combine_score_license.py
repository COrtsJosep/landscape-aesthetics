import pandas as pd
import os

folder_path_1 = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_raw/'
folder_path_2 = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_score/'
output_folder = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/'

num_files = 100

for i in range(num_files):

    file_index = str(i).zfill(2)

    file_1 = os.path.join(folder_path_1, f'ns6_clean_{file_index}.csv')
    file_2 = os.path.join(folder_path_2, f'processed_ns6_clean_{file_index}.csv')
    
    # read two files
    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)
    
    # merge based on image_path
    merged_df = pd.merge(df1, df2, on='image_path', how='inner')
    
    # save to new file
    output_file = os.path.join(output_folder, f'merged_ns6_clean_{file_index}.csv')
    merged_df.to_csv(output_file, index=False)
    
    print(f'{file_1} and {file_2} have been merged and saved as {output_file}')
