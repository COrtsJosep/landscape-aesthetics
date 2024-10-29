import pandas as pd

file_path = '/home/ubuntu/landscape-aesthetics/data/processed/wikimedia_commons/clean/ns6_clean_00.parquet'
df = pd.read_parquet(file_path)

# print(df.columns)

# print(df.columns.tolist())

copyright_columns = ['license', 'url', 'copyrighted', 'attribution_required', 'attribution', 'ns6_unnormalized_title']
copyright_info = df[copyright_columns]


print(copyright_info.head())