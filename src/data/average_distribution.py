import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
import seaborn as sns

# read file
file_path = '/home/ubuntu/landscape-aesthetics/data/external/scenicornot/votes.tsv'  # Replace with your actual file path
df = pd.read_csv(file_path, sep='\t')

average_data = df['Average']

# # histogram
# plt.figure(figsize=(8, 6))
# plt.hist(average_data, bins=200, color='#1E90FF', alpha=0.7)
# plt.xticks(range(1, 11, 1))
# plt.xlabel('Average Scores')
# plt.ylabel('Frequency')
# plt.grid(axis='y')
# plt.savefig("average_score_distribution.png", format="png", dpi=300, bbox_inches="tight") 
# plt.show()

# KDE density graph
sns.kdeplot(df['Average'], shade=True, color='#1E90FF', bw_adjust=0.3)
plt.xlabel('Average Score')
plt.ylabel('Density')
plt.title('Density Plot of Average Scores with Lower Bandwidth')
plt.savefig("average_score_density.png", format="png", dpi=300, bbox_inches="tight")  
plt.show()