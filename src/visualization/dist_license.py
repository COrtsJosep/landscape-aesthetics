import pandas as pd
import os

folder_path = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/'
file_names = [f'merged_ns6_clean_{str(i).zfill(2)}.csv' for i in range(100)]

all_licenses = set()

# Loop through each file to collect unique licenses
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)

    # Add unique licenses from the current file to the set
    all_licenses.update(df['license'].dropna().unique())

# Display all distinct license values
print("Distinct license values:")
for license in all_licenses:
    print(license)
