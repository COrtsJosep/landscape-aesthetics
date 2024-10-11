import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

file_path = '/home/ubuntu/landscape-aesthetics/data/external/scenicornot/votes.tsv'  # Replace with your actual file path
df = pd.read_csv(file_path, sep='\t')

average_data = df['Average']

plt.figure(figsize=(8, 6))

plt.hist(average_data, bins=200, color='#1E90FF', alpha=0.7)  

plt.xticks(range(1, 11, 1))  

plt.xlabel('Average Scores')
plt.ylabel('Frequency')
# plt.title('Frequency Distribution of Average Scores')
plt.grid(axis='y')

plt.show()